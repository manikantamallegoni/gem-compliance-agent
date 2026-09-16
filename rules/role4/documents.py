from app.models import BidderData, TenderRules
from .common import result, today


def check_certificate(bidder: BidderData, tender: TenderRules):
    if not tender.certificate_required:
        return result(
            "R007", "Certificate Requirement", "NOT_REQUIRED",
            "Certificate is not required by this tender."
        )

    if bidder.certificate_status.lower() == "missing":
        return result(
            "R007", "Certificate Requirement", "MISSING",
            "Required certificate information was not provided.",
            "HIGH"
        )

    status = bidder.certificate_status.lower()

    if status in {"valid", "active"}:
        return result(
            "R007", "Certificate Requirement", "PASS",
            "Required certificate is marked as valid."
        )

    if status in {"pending", "unclear", "review"}:
        return result(
            "R007", "Certificate Requirement", "REVIEW",
            "Certificate requires manual verification.",
            "MEDIUM"
        )

    return result(
        "R007", "Certificate Requirement", "FAIL",
        "Certificate verification failed.",
        "HIGH"
    )


def check_document_expiry(bidder: BidderData, tender: TenderRules):
    if not bidder.document_expiry_date:
        return result(
            "R009", "Document Expiry", "REVIEW",
            "No document expiry date was supplied for date validation.",
            "MEDIUM"
        )

    if bidder.document_expiry_date < today():
        return result(
            "R009", "Document Expiry", "FAIL",
            f"Document expired on {bidder.document_expiry_date.isoformat()}.",
            "HIGH", field="document_expiry_date",
            value=bidder.document_expiry_date.isoformat()
        )

    return result(
        "R009", "Document Expiry", "PASS",
        f"Document remains valid until {bidder.document_expiry_date.isoformat()}.",
        field="document_expiry_date",
        value=bidder.document_expiry_date.isoformat()
    )
