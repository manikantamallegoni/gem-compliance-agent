from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Evidence(BaseModel):
    source: str = "Provided bidder data"
    page: Optional[int] = None
    field: Optional[str] = None
    value: Optional[str] = None


class BidderData(BaseModel):
    model_config = ConfigDict(extra="allow")

    company_name: str

    pan: Optional[str] = None
    pan_status: str = "Missing"

    gst: Optional[str] = None
    gst_status: str = "Missing"

    udyam: Optional[str] = None
    udyam_status: str = "Missing"

    turnover: float = 0
    oem_status: str = "Missing"

    blacklisted: bool = False

    startup_status: str = "Not Applicable"
    nsic_status: str = "Not Applicable"
    make_in_india_status: str = "Not Applicable"
    epfo_status: str = "Not Applicable"
    esic_status: str = "Not Applicable"

    certificate_status: str = "Missing"
    document_expiry_date: Optional[date] = None

    company_name_pan: Optional[str] = None
    company_name_gst: Optional[str] = None
    company_name_udyam: Optional[str] = None
    company_name_oem: Optional[str] = None

    @classmethod
    def from_json_file(cls, path: str):
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))


class TenderRules(BaseModel):
    tender_id: str = "UNKNOWN"

    gst_required: bool = True
    pan_required: bool = True
    udyam_required: bool = False
    oem_required: bool = False
    startup_required: bool = False
    nsic_required: bool = False
    make_in_india_required: bool = False
    epfo_required: bool = False
    esic_required: bool = False
    certificate_required: bool = False

    minimum_turnover: float = 0

    @classmethod
    def from_json_file(cls, path: str):
        return cls(**json.loads(Path(path).read_text(encoding="utf-8")))


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    status: str
    severity: str = "INFO"
    reason: str
    evidence: list[Evidence] = Field(default_factory=list)


class ComplianceReport(BaseModel):
    bidder_name: str
    tender_id: str
    results: list[RuleResult]
    compliance_score: float
    risk_level: str
    recommendation: str
    review_required: bool
    summary: dict
    audit_trail: list[dict]
