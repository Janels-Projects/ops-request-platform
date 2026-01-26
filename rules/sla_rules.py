
from datetime import datetime

# SLA thresholds in HOURS by priority
# Phase 1: Resolution SLA only (read-only, computed)
SLA_RULES = {
    "low": {
        "resolution_hours": 120,  # 5 days
    },
    "medium": {
        "resolution_hours": 72,   # 3 days
    },
    "high": {
        "resolution_hours": 48,   # 2 days
    },
}


def compute_sla_status(request):
    """
    Compute SLA status for a request row.
    Returns None if SLA does not apply.
    """

    status = request["status"]
    priority = request["priority"]

    # SLA only applies to active requests
    if status not in ("pending", "in_progress"):
        return None

    rule = SLA_RULES.get(priority)
    if not rule:
        return None

    created_at = datetime.fromisoformat(request["created_at"])
    now = datetime.utcnow()

    age_hours = (now - created_at).total_seconds() / 3600
    target_hours = rule["resolution_hours"]
    remaining_hours = target_hours - age_hours

    return {
        "breached": remaining_hours < 0,
        "remaining_hours": max(0, int(remaining_hours)),
        "target_hours": target_hours,
    }
