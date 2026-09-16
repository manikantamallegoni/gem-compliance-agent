from app.models import BidderData, TenderRules, ComplianceReport
from app.rules.identity import check_pan, check_company_name_consistency
from app.rules.registrations import (
    check_gst,
    check_udyam,
    check_oem,
    check_startup,
    check_nsic,
    check_make_in_india,
    check_epfo,
    check_esic,
)
from app.rules.financial import check_turnover
from app.rules.eligibility import check_blacklist
from app.rules.documents import check_certificate, check_document_expiry
from app.scoring import calculate_score, risk_level, summary_counts
from app.audit import build_audit_trail


def generate_recommendation(results, score, risk):
    if any(r.rule_id == "R006" and r.status == "FAIL" for r in results):
        return "HIGH RISK - FURTHER VERIFICATION REQUIRED"

    if any(r.status == "CONFLICT" for r in results):
        return "REVIEW REQUIRED - DOCUMENT CONFLICT DETECTED"

    if any(r.status == "FAIL" for r in results):
        return "REVIEW REQUIRED - COMPLIANCE FAILURE"

    if any(r.status == "MISSING" for r in results):
        return "REVIEW REQUIRED - MISSING INFORMATION"

    if any(r.status == "REVIEW" for r in results):
        return "REVIEW REQUIRED - MANUAL VERIFICATION NEEDED"

    if score >= 90:
        return "RECOMMENDED FOR FURTHER EVALUATION"

    return f"REVIEW REQUIRED - RISK LEVEL {risk}"


def run_compliance_check(
    bidder: BidderData,
    tender: TenderRules
) -> ComplianceReport:

    results = [
        check_gst(bidder, tender),
        check_pan(bidder, tender),
        check_udyam(bidder, tender),
        check_turnover(bidder, tender),
        check_oem(bidder, tender),
        check_blacklist(bidder, tender),
        check_certificate(bidder, tender),
        check_company_name_consistency(bidder, tender),
        check_document_expiry(bidder, tender),
        check_startup(bidder, tender),
        check_nsic(bidder, tender),
        check_make_in_india(bidder, tender),
        check_epfo(bidder, tender),
        check_esic(bidder, tender),
    ]

    score = calculate_score(results)
    risk = risk_level(score, results)
    recommendation = generate_recommendation(results, score, risk)

    review_required = any(
        r.status in {"REVIEW", "MISSING", "CONFLICT", "FAIL"}
        for r in results
    )

    return ComplianceReport(
        bidder_name=bidder.company_name,
        tender_id=tender.tender_id,
        results=results,
        compliance_score=score,
        risk_level=risk,
        recommendation=recommendation,
        review_required=review_required,
        summary=summary_counts(results),
        audit_trail=build_audit_trail(results),
    )
