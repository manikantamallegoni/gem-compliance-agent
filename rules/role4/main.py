from fastapi import FastAPI
from app.models import BidderData, TenderRules, ComplianceReport
from app.engine import run_compliance_check

app = FastAPI(
    title="SIH 26100 - Role 4 Compliance Engine",
    version="1.0.0",
    description=(
        "Rules and Decision Engine for bidder compliance verification. "
        "Decision-support only; final procurement decision remains with the officer."
    ),
)


@app.get("/")
def root():
    return {
        "project": "SIH 26100",
        "module": "Role 4 - Rules & Decision Engine",
        "status": "running",
        "api_version": "v1",
        "endpoint": "/api/v1/compliance/check",
    }


@app.post("/api/v1/compliance/check", response_model=ComplianceReport)
def compliance_check(
    bidder: BidderData,
    tender: TenderRules,
):
    return run_compliance_check(bidder, tender)


@app.get("/api/v1/demo", response_model=ComplianceReport)
def demo():
    bidder = BidderData.from_json_file("data/sample_bidder.json")
    tender = TenderRules.from_json_file("data/sample_tender_rules.json")
    return run_compliance_check(bidder, tender)
