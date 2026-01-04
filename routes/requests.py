from flask import Blueprint, redirect, url_for, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection
from flask import request, abort, redirect, url_for
from rules.request_rules import VALID_CATEGORIES


requests_bp = Blueprint(
    "requests",
    __name__,
    url_prefix="/dashboard"
)

@requests_bp.post("/requests/<int:request_id>/review")
@jwt_required()
def review_request(request_id):
    admin_id = int(get_jwt_identity())

    action = request.form.get("action")
    admin_review_notes = request.form.get("admin_review_notes")
    
    # 🔥 REMOVED "start" from valid actions since we don't need it anymore
    if action not in ("approve", "deny", "complete"):
        abort(400, "Invalid action")

    # 🔥 CHANGED: Approve now goes directly to "in_progress"
    if action == "approve":
        new_status = "in_progress"  # Skip "approved" status

    elif action == "deny":
        new_status = "denied"

    else:  # action == "complete"
        new_status = "completed"

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure admin role
    cursor.execute(
        "SELECT role FROM users WHERE id = ?",
        (admin_id,)
    )
    admin = cursor.fetchone()

    if not admin or admin["role"] != "admin":
        abort(403)

    # Fetch current request status
    cursor.execute(
        "SELECT status FROM requests WHERE id = ?",
        (request_id,)
    )
    row = cursor.fetchone()

    if not row:
        abort(404, "Request not found")

    current_status = row["status"]

    # 🔒 LIFECYCLE ENFORCEMENT
    if not validate_transition(current_status, new_status, "admin"):
        abort(409, "Invalid status transition")

    # ✅ Perform update only if valid
    if admin_review_notes:
        cursor.execute(
        """
        UPDATE requests
        SET status = ?,
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = ?,
            admin_review_notes = ?
        WHERE id = ?
        """,
        (new_status, admin_id, admin_review_notes, request_id)
    )
    else:
        cursor.execute(
        """
        UPDATE requests
        SET status = ?,
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = ?
        WHERE id = ?
        """,
        (new_status, admin_id, request_id)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.admin_dashboard"))


# Create Request Route
@requests_bp.post("/requests")
@jwt_required()
def create_request():
    user_id = int(get_jwt_identity())

    request_type = request.form.get("request_type")
    category = request.form.get("category")
    priority = request.form.get("priority", "medium")

    if not request_type or not category:
        abort(400, "Missing required fields")

    # ✅ Backend category validation
    if category not in VALID_CATEGORIES:
        abort(400, "Invalid category")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Ensure user is NOT admin
    cursor.execute(
        "SELECT role FROM users WHERE id = ?",
        (user_id,)
    )
    user = cursor.fetchone()

    if not user or user["role"] != "user":
        abort(403)

    cursor.execute(
        """
        INSERT INTO requests (
            user_id,
            request_type,
            category,
            priority,
            status
        )
        VALUES (?, ?, ?, ?, 'pending')
        """,
        (user_id, request_type, category, priority)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")



# Transition Validator 
ALLOWED_TRANSITIONS = {
    "user": {
        "pending": {"cancelled"},
        "approved": {"cancelled"},
        "in_progress": {"cancelled"},  # Users can cancel in-progress requests too
    },
    "admin": {
        "pending": {"approved", "denied", "in_progress"},  # 🔥 ADDED: in_progress
        "approved": {"in_progress"},  # Keep this for backwards compatibility
        "in_progress": {"completed"},
    }
}

def validate_transition(current_status, new_status, actor_role):
    allowed = ALLOWED_TRANSITIONS.get(actor_role, {})
    return new_status in allowed.get(current_status, set())

