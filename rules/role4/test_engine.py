from datetime import date

from app.engine import run_compliance_check
from app.models import BidderData, TenderRules


def base_bidder():
    return BidderData(
        company_name="ABC Technologies Pvt Ltd",
        pan="ABCDE1234F",
        pan_status="Valid",
        gst="29ABCDE1234F1Z5",
        gst_status="Active",
        udyam="UDYAM-TS-01-1234567",
        udyam_status="Active",
        turnover=150000000,
        oem_status="Valid",
        blacklisted=False,
        certificate_status="Valid",
        document_expiry_date=date(2027, 12, 31),
        company_name_pan="ABC Technologies Pvt Ltd",
        company_name_gst="ABC Technologies Pvt Ltd",
        company_name_udyam="ABC Technologies Pvt Ltd",
        company_name_oem="ABC Technologies Pvt Ltd",
    )


def base_tender():
    return TenderRules(
        tender_id="TEST",
        gst_required=True,
        pan_required=True,
        udyam_required=True,
        oem_required=True,
        certificate_required=True,
        minimum_turnover=100000000,
    )


def statuses(report):
    return {x.rule_id: x.status for x in report.results}


def test_all_pass():
    report = run_compliance_check(base_bidder(), base_tender())
    s = statuses(report)

    assert s["R001"] == "PASS"
    assert s["R002"] == "PASS"
    assert s["R003"] == "PASS"
    assert s["R004"] == "PASS"
    assert s["R006"] == "PASS"


def test_turnover_fail():
    bidder = base_bidder()
    bidder.turnover = 50000000

    report = run_compliance_check(bidder, base_tender())

    assert statuses(report)["R004"] == "FAIL"
    assert "COMPLIANCE FAILURE" in report.recommendation


def test_missing_gst():
    bidder = base_bidder()
    bidder.gst = None
    bidder.gst_status = "Missing"

    report = run_compliance_check(bidder, base_tender())

    assert statuses(report)["R001"] == "MISSING"
    assert report.review_required is True


def test_blacklist_is_critical():
    bidder = base_bidder()
    bidder.blacklisted = True

    report = run_compliance_check(bidder, base_tender())

    assert statuses(report)["R006"] == "FAIL"
    assert report.risk_level == "CRITICAL"


def test_company_conflict():
    bidder = base_bidder()
    bidder.company_name_gst = "XYZ Technologies Pvt Ltd"

    report = run_compliance_check(bidder, base_tender())

    assert statuses(report)["R008"] == "CONFLICT"
    assert "CONFLICT" in report.recommendation


def test_expired_document():
    bidder = base_bidder()
    bidder.document_expiry_date = date(2020, 1, 1)

    report = run_compliance_check(bidder, base_tender())

    assert statuses(report)["R009"] == "FAIL"


def test_not_required_rule():
    tender = base_tender()
    tender.udyam_required = False

    report = run_compliance_check(base_bidder(), tender)

    assert statuses(report)["R003"] == "NOT_REQUIRED"
