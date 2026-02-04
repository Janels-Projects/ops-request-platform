
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
    Returns string status: 'on_time', 'at_risk', or 'overdue'
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

    # Return simple string status
    if remaining_hours < 0:
        return "overdue"
    elif remaining_hours < target_hours * 0.25:  # Less than 25% time remaining
        return "at_risk"
    else:
        return "on_time"


def did_meet_sla(request):
    """
    Returns True if a completed request met SLA deadline.
    """
    from datetime import datetime

    if request["status"] != "completed":
        return None

    priority = request["priority"]
    rule = SLA_RULES.get(priority)
    if not rule:
        return None

    created_at = datetime.fromisoformat(request["created_at"])
    reviewed_at = datetime.fromisoformat(request["reviewed_at"])

    elapsed_hours = (reviewed_at - created_at).total_seconds() / 3600
    target_hours = rule["resolution_hours"]

    return elapsed_hours <= target_hours

