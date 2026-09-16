from datetime import date
from app.models import Evidence, RuleResult

STATUSES = {
    "PASS",
    "FAIL",
    "REVIEW",
    "MISSING",
    "CONFLICT",
    "NOT_REQUIRED",
}

def result(
    rule_id: str,
    rule_name: str,
    status: str,
    reason: str,
    severity: str = "INFO",
    source: str = "Provided bidder data",
    field: str | None = None,
    value: str | None = None,
):
    if status not in STATUSES:
        raise ValueError(f"Invalid compliance status: {status}")

    evidence = []
    if field or value:
        evidence.append(
            Evidence(source=source, field=field, value=value)
        )

    return RuleResult(
        rule_id=rule_id,
        rule_name=rule_name,
        status=status,
        severity=severity,
        reason=reason,
        evidence=evidence,
    )


def normalize_name(name: str | None) -> str:
    if not name:
        return ""
    return " ".join(
        name.lower()
        .replace(",", " ")
        .replace(".", " ")
        .split()
    )


def today() -> date:
    return date.today()
