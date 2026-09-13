"""
Pydantic Schemas for Request/Response validation and LLM Structured Outputs.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class ComplianceStatus(str, Enum):
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"


class EvaluationRequest(BaseModel):
    tender_id: str = Field(..., example="GEM/2026/B/2002")
    bidder_name: str = Field(..., example="Tech Corp")
    tender_requirements: str = Field(
        ..., example="Minimum turnover of 50 Lakhs INR required. GSTIN mandatory."
    )
    bidder_document_text: str = Field(
        ..., example="Bidder turnover is 85 Lakhs INR. GSTIN: 36ABCDE1234F1ZH."
    )


class ClauseEvaluation(BaseModel):
    clause_id: str = Field(..., description="Unique ID for requirement clause")
    requirement_name: str = Field(..., description="Brief name of requirement")
    status: ComplianceStatus = Field(..., description="Evaluation status result")
    expected_value: Optional[str] = Field(None, description="Tender baseline value")
    actual_value: Optional[str] = Field(None, description="Found value in bidder doc")
    evidence: Optional[str] = Field(None, description="Exact text excerpt supporting status")
    reasoning: str = Field(..., description="LLM logic explaining evaluation outcome")


class ComplianceReport(BaseModel):
    tender_id: Optional[str] = Field(None, description="Associated Tender ID")
    bidder_name: Optional[str] = Field(None, description="Evaluated Bidder Name")
    overall_status: ComplianceStatus = Field(..., description="Final overall verdict")
    summary: str = Field(..., description="High-level executive summary")
    evaluations: List[ClauseEvaluation] = Field(
        default_factory=list, description="Per-clause granular evaluations"
    )