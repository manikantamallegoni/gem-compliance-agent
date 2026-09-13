from __future__ import annotations

"""
FastAPI Router for GeM Compliance Agent Endpoints.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from agent.compliance_agent import GeMComplianceAgent
from agent.schema import ComplianceReport, EvaluationRequest
from document_intelligence.extractor import extract_text_from_file

logger = logging.getLogger("agent.router")

router = APIRouter(prefix="/agent", tags=["GeM Compliance Agent"])
agent = GeMComplianceAgent()


@router.post("/evaluate", response_model=ComplianceReport)
def evaluate_compliance(request: EvaluationRequest) -> ComplianceReport:
    """
    Evaluate compliance directly using raw JSON text input.
    """
    try:
        return agent.evaluate(request)
    except Exception as exc:
        logger.error("Error during JSON evaluation: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance evaluation failed: {str(exc)}",
        ) from exc


@router.post("/evaluate-file", response_model=ComplianceReport)
async def evaluate_compliance_file(
        tender_id: Annotated[str, Form(...)],
        bidder_name: Annotated[str, Form(...)],
        tender_requirements: Annotated[str, Form(...)],
        file: Annotated[UploadFile, File(...)],
) -> ComplianceReport:
    """
    Evaluate compliance from an uploaded bidder document (.pdf, .docx, or .txt).
    """
    try:
        document_text = await extract_text_from_file(file)

        request = EvaluationRequest(
            tender_id=tender_id,
            bidder_name=bidder_name,
            tender_requirements=tender_requirements,
            bidder_document_text=document_text,
        )

        return agent.evaluate(request)

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve),
        ) from ve
    except Exception as exc:
        logger.error("Error during file evaluation: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File compliance evaluation failed: {str(exc)}",
        ) from exc