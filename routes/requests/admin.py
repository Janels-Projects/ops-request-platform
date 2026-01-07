from flask import request, redirect, url_for, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import requests_bp
from routes.auth import admin_required
from models.db import get_db_connection
from rules.request_rules import validate_transition



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
