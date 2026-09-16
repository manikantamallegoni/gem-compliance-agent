from app.models import BidderData, TenderRules
from .common import normalize_name, result


def check_company_name_consistency(
    bidder: BidderData, tender: TenderRules
):
    pairs = {
        "PAN": bidder.company_name_pan,
        "GST": bidder.company_name_gst,
        "Udyam": bidder.company_name_udyam,
        "OEM": bidder.company_name_oem,
    }

    available = {
        source: normalize_name(name)
        for source, name in pairs.items()
        if name
    }

    if len(available) < 2:
        return result(
            "R008",
            "Company Name Consistency",
            "REVIEW",
            "Not enough document names were provided for cross-document comparison.",
            "MEDIUM",
        )

    unique_names = set(available.values())

    if len(unique_names) == 1:
        return result(
            "R008",
            "Company Name Consistency",
            "PASS",
            "Company name is consistent across the available documents.",
        )

    details = ", ".join(
        f"{source}='{name}'" for source, name in pairs.items() if name
    )

    return result(
        "R008",
        "Company Name Consistency",
        "CONFLICT",
        f"Company name mismatch detected: {details}",
        "HIGH",
    )


def check_pan(bidder: BidderData, tender: TenderRules):
    if not tender.pan_required:
        return result(
            "R002", "PAN Verification", "NOT_REQUIRED",
            "PAN is not required by this tender."
        )

    if not bidder.pan or bidder.pan_status.lower() == "missing":
        return result(
            "R002", "PAN Verification", "MISSING",
            "PAN information was not provided.",
            "HIGH"
        )

    status = bidder.pan_status.lower()

    if status == "valid":
        return result(
            "R002", "PAN Verification", "PASS",
            "PAN is marked as valid.",
            field="pan", value=bidder.pan
        )

    if status in {"unclear", "pending", "review"}:
        return result(
            "R002", "PAN Verification", "REVIEW",
            "PAN requires manual verification.",
            "MEDIUM", field="pan", value=bidder.pan
        )

    return result(
        "R002", "PAN Verification", "FAIL",
        "PAN verification failed.",
        "HIGH", field="pan", value=bidder.pan
    )
