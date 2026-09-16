from app.models import BidderData, TenderRules
from .common import result


def _status_rule(value, required, rule_id, name, document, field):
    if not required:
        return result(rule_id, name, "NOT_REQUIRED",
                      f"{document} is not required by this tender.")

    if not value or value.lower() == "missing":
        return result(rule_id, name, "MISSING",
                      f"{document} information was not provided.", "HIGH")

    status = value.lower()

    if status in {"active", "valid", "compliant", "verified"}:
        return result(rule_id, name, "PASS",
                      f"{document} status is {value}.",
                      field=field, value=value)

    if status in {"pending", "unclear", "review"}:
        return result(rule_id, name, "REVIEW",
                      f"{document} requires manual verification.",
                      "MEDIUM", field=field, value=value)

    return result(rule_id, name, "FAIL",
                  f"{document} verification failed.",
                  "HIGH", field=field, value=value)


def check_gst(bidder, tender):
    return _status_rule(
        bidder.gst_status, tender.gst_required,
        "R001", "GST Verification", "GST registration", "gst_status"
    )


def check_udyam(bidder, tender):
    return _status_rule(
        bidder.udyam_status, tender.udyam_required,
        "R003", "Udyam/MSME Verification", "Udyam registration", "udyam_status"
    )


def check_oem(bidder, tender):
    return _status_rule(
        bidder.oem_status, tender.oem_required,
        "R005", "OEM Authorization", "OEM authorization", "oem_status"
    )


def check_startup(bidder, tender):
    return _status_rule(
        bidder.startup_status, tender.startup_required,
        "R010", "Startup India Verification", "Startup India status", "startup_status"
    )


def check_nsic(bidder, tender):
    return _status_rule(
        bidder.nsic_status, tender.nsic_required,
        "R011", "NSIC Verification", "NSIC status", "nsic_status"
    )


def check_make_in_india(bidder, tender):
    return _status_rule(
        bidder.make_in_india_status, tender.make_in_india_required,
        "R012", "Make in India Compliance", "Make in India status", "make_in_india_status"
    )


def check_epfo(bidder, tender):
    return _status_rule(
        bidder.epfo_status, tender.epfo_required,
        "R013", "EPFO Compliance", "EPFO compliance", "epfo_status"
    )


def check_esic(bidder, tender):
    return _status_rule(
        bidder.esic_status, tender.esic_required,
        "R014", "ESIC Compliance", "ESIC compliance", "esic_status"
    )
