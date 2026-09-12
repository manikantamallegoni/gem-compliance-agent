from app.models import BidderData, TenderRules
from .common import result


def check_turnover(bidder: BidderData, tender: TenderRules):
    required = tender.minimum_turnover
    actual = bidder.turnover

    if required <= 0:
        return result(
            "R004", "Minimum Turnover", "NOT_REQUIRED",
            "No minimum turnover requirement was configured."
        )

    if actual is None or actual <= 0:
        return result(
            "R004", "Minimum Turnover", "MISSING",
            "Turnover information was not provided.",
            "HIGH"
        )

    actual_cr = actual / 10_000_000
    required_cr = required / 10_000_000

    if actual >= required:
        return result(
            "R004", "Minimum Turnover", "PASS",
            f"Turnover ₹{actual_cr:.2f} Cr meets the required ₹{required_cr:.2f} Cr.",
            field="turnover", value=str(actual)
        )

    return result(
        "R004", "Minimum Turnover", "FAIL",
        f"Turnover ₹{actual_cr:.2f} Cr is below the required ₹{required_cr:.2f} Cr.",
        "HIGH", field="turnover", value=str(actual)
    )
