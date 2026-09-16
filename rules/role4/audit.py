from datetime import datetime, timezone


def build_audit_trail(results):
    timestamp = datetime.now(timezone.utc).isoformat()

    trail = []

    for item in results:
        trail.append({
            "timestamp": timestamp,
            "rule_id": item.rule_id,
            "rule_name": item.rule_name,
            "status": item.status,
            "severity": item.severity,
            "reason": item.reason,
            "evidence": [e.model_dump() for e in item.evidence],
        })

    return trail
