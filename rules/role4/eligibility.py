from app.models import BidderData, TenderRules
from .common import result


def check_blacklist(bidder: BidderData, tender: TenderRules):
    if bidder.blacklisted:
        return result(
            "R006", "Blacklist / Debarment", "FAIL",
            "Bidder is marked as blacklisted/debarred and requires immediate review.",
            "CRITICAL", field="blacklisted", value="true"
        )

    return result(
        "R006", "Blacklist / Debarment", "PASS",
        "Bidder is not marked as blacklisted/debarred.",
        field="blacklisted", value="false"
    )
