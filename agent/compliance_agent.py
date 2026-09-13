from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypedDict

from agent.config import settings
from agent.prompts import (
    GEM_COMPLIANCE_SYSTEM_PROMPT,
    build_evaluation_user_prompt,
)
from agent.schema import (
    ClauseEvaluation,
    ComplianceReport,
    ComplianceStatus,
    EvaluationRequest,
)
from agent.tools import (
    get_tender_rules,
    verify_document_credentials,
    verify_turnover,
)
from langgraph.graph import END, StateGraph

logger = logging.getLogger("agent.compliance_agent")


# --- State Definition ---
class AgentState(TypedDict):
    request: EvaluationRequest
    rules: List[Dict[str, Any]]
    verification_results: Dict[str, Any]
    report: Optional[ComplianceReport]


class GeMComplianceAgent:
    """
    Orchestrates compliance evaluation via a stateful LangGraph workflow.
    """

    def __init__(self, model: Optional[str] = None) -> None:
        self.model_name = model or settings.default_model
        self.graph = self._build_graph()

    # --- Node 1: Fetch Rules ---
    def _fetch_rules_node(self, state: AgentState) -> Dict[str, Any]:
        rules = get_tender_rules(state["request"].tender_id)
        return {"rules": rules}

    # --- Node 2: Run Verification Tools ---
    def _verify_data_node(self, state: AgentState) -> Dict[str, Any]:
        doc_text = state["request"].bidder_document_text or ""

        # Run credential verification (GSTIN, PAN, Udyam regex checks)
        credentials_check = verify_document_credentials(doc_text)

        # Run turnover verification check
        turnover_check = verify_turnover("50 Lakhs INR", doc_text)

        verification_results = {
            "credentials": credentials_check,
            "turnover": turnover_check,
        }

        return {"verification_results": verification_results}

    # --- Node 3: Structured LLM Evaluation ---
    def _evaluate_llm_node(self, state: AgentState) -> Dict[str, Any]:
        req = state["request"]
        verif_results = state.get("verification_results", {})

        try:
            api_key = settings.openrouter_api_key or settings.openai_api_key
            base_url = (
                "https://openrouter.ai/api/v1"
                if settings.openrouter_api_key
                else None
            )

            if not api_key:
                logger.warning("No API key set. Using fallback report.")
                return {"report": self._build_mock_report(req, state["rules"])}

            from langchain_openai import ChatOpenAI

            selected_model = self.model_name
            if settings.openrouter_api_key and "/" not in selected_model:
                selected_model = f"openai/{selected_model}"

            llm_kwargs = {
                "model": selected_model,
                "api_key": api_key,
                "temperature": 0,
            }
            if base_url:
                llm_kwargs["base_url"] = base_url

            llm = ChatOpenAI(**llm_kwargs)

            # Combine verified credentials & prompt context
            raw_user_prompt = build_evaluation_user_prompt(
                tender_requirements=req.tender_requirements,
                bidder_document_text=req.bidder_document_text,
                tender_id=req.tender_id,
                bidder_name=req.bidder_name,
            )

            contextualized_prompt = (
                f"{raw_user_prompt}\n\n"
                f"### DETERMINISTIC VERIFICATION RESULTS:\n{verif_results}"
            )

            messages = [
                {"role": "system", "content": GEM_COMPLIANCE_SYSTEM_PROMPT},
                {"role": "user", "content": contextualized_prompt},
            ]

            # Use structured output with method fallback to function calling
            try:
                structured_llm = llm.with_structured_output(
                    ComplianceReport, method="function_calling"
                )
                report = structured_llm.invoke(messages)
            except Exception:
                structured_llm = llm.with_structured_output(ComplianceReport)
                report = structured_llm.invoke(messages)

            if not report.tender_id and req.tender_id:
                report.tender_id = req.tender_id
            if not report.bidder_name and req.bidder_name:
                report.bidder_name = req.bidder_name

            return {"report": report}

        except Exception as exc:
            logger.warning("LangGraph LLM Node failed (%s); returning mock.", exc)
            return {"report": self._build_mock_report(req, state["rules"])}

    # --- LangGraph Graph Construction ---
    def _build_graph(self):
        builder = StateGraph(AgentState)

        builder.add_node("fetch_rules", self._fetch_rules_node)
        builder.add_node("verify_data", self._verify_data_node)
        builder.add_node("evaluate_llm", self._evaluate_llm_node)

        builder.set_entry_point("fetch_rules")
        builder.add_edge("fetch_rules", "verify_data")
        builder.add_edge("verify_data", "evaluate_llm")
        builder.add_edge("evaluate_llm", END)

        return builder.compile()

    # --- Execution Pipeline ---
    def evaluate(self, request: EvaluationRequest) -> ComplianceReport:
        initial_state: AgentState = {
            "request": request,
            "rules": [],
            "verification_results": {},
            "report": None,
        }

        final_state = self.graph.invoke(initial_state)
        return final_state["report"]

    # --- Fallback Mock Builder ---
    def _build_mock_report(
            self, request: EvaluationRequest, rules: List[Dict[str, Any]]
    ) -> ComplianceReport:
        evaluations = []
        for rule in rules:
            evaluations.append(
                ClauseEvaluation(
                    clause_id=rule.get("clause_id", "UNKNOWN"),
                    requirement_name=rule.get("requirement_name", "Requirement"),
                    status=ComplianceStatus.NEEDS_HUMAN_REVIEW,
                    expected_value=rule.get("expected_value"),
                    actual_value=None,
                    evidence=None,
                    reasoning="Flagged for human review.",
                )
            )

        return ComplianceReport(
            tender_id=request.tender_id,
            bidder_name=request.bidder_name,
            overall_status=ComplianceStatus.NEEDS_HUMAN_REVIEW,
            summary="Fallback evaluation completed.",
            evaluations=evaluations,
        )