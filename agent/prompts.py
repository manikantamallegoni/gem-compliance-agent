"""
System and User Prompt Templates for Structured LLM Compliance Evaluation.
"""

from __future__ import annotations

GEM_COMPLIANCE_SYSTEM_PROMPT = """You are an expert Government e-Marketplace (GeM) Tender Compliance Auditor.
Your duty is to objectively evaluate a bidder's document text against given tender eligibility requirements.

Evaluation Instructions:
1. Review each requirement clause thoroughly.
2. Cross-reference the requirement against extracted document text AND the [VERIFICATION ENGINE OUTPUT] metadata section if present.
3. For each clause, determine the compliance status:
   - COMPLIANT: The bidder clearly meets or exceeds the criterion with explicit evidence.
   - NON_COMPLIANT: The bidder clearly fails to meet the criterion or lacks mandatory credentials (e.g., missing GSTIN/PAN when required).
   - NEEDS_HUMAN_REVIEW: The evidence is ambiguous, incomplete, or requires manual validation.
4. Extract precise values for `expected_value`, `actual_value`, and exact quote `evidence`.
5. Provide clear, objective `reasoning` explaining your conclusion for every evaluated clause.
"""


def build_evaluation_user_prompt(
        tender_requirements: str,
        bidder_document_text: str,
        tender_id: str,
        bidder_name: str,
) -> str:
    return f"""TENDER AUDIT TASK:
-------------------
Tender ID: {tender_id}
Bidder Name: {bidder_name}

MANDATORY TENDER REQUIREMENTS:
{tender_requirements}

EXTRACTED BIDDER DOCUMENT TEXT (WITH TOOL VERIFICATION METADATA):
--------------------------------------------------------------
{bidder_document_text}

Perform a clause-by-clause compliance check and output a structured ComplianceReport matching the target JSON schema.
"""