from collections import Counter

# Weight can be changed by the team as tender policy evolves.
DEFAULT_WEIGHTS = {
    "R001": 15,  # GST
    "R002": 15,  # PAN
    "R003": 10,  # Udyam
    "R004": 20,  # Turnover
    "R005": 10,  # OEM
    "R006": 20,  # Blacklist
    "R007": 5,   # Certificate
    "R008": 5,   # Name consistency
    "R009": 5,   # Expiry
    "R010": 5,
    "R011": 5,
    "R012": 5,
    "R013": 5,
    "R014": 5,
}

def calculate_score(results):
    applicable = [
        item for item in results
        if item.status != "NOT_REQUIRED"
    ]

    if not applicable:
        return 0.0

    total_weight = sum(DEFAULT_WEIGHTS.get(item.rule_id, 5) for item in applicable)

    if total_weight == 0:
        return 0.0

    earned = 0

    for item in applicable:
        weight = DEFAULT_WEIGHTS.get(item.rule_id, 5)

        if item.status == "PASS":
            earned += weight
        elif item.status == "REVIEW":
            earned += weight * 0.5
        # FAIL, MISSING and CONFLICT earn 0

    return round((earned / total_weight) * 100, 2)


def risk_level(score, results):
    if any(item.status == "FAIL" and item.rule_id == "R006" for item in results):
        return "CRITICAL"

    if any(item.status == "CONFLICT" for item in results):
        return "HIGH"

    if score >= 90:
        return "LOW"
    if score >= 75:
        return "MEDIUM"
    if score >= 50:
        return "HIGH"
    return "CRITICAL"


def summary_counts(results):
    return dict(Counter(item.status for item in results))
