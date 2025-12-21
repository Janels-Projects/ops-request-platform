from flask import Blueprint, redirect, url_for, request, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection
from flask import request, abort, redirect, url_for

requests_bp = Blueprint(
    "requests",
    __name__,
    url_prefix="/dashboard"
)

@requests_bp.post("/requests/<int:request_id>/approve")
@jwt_required()
def approve_request(request_id):
    admin_id = int(get_jwt_identity())

    conn = get_db_connection()
    conn.execute("""
        UPDATE requests
        SET status = 'approved',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = ?
        WHERE id = ?
    """, (admin_id, request_id))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.admin_dashboard"))


@requests_bp.post("/requests/<int:request_id>/deny")
@jwt_required()
def deny_request(request_id):
    admin_id = int(get_jwt_identity())

    conn = get_db_connection()
    conn.execute("""
        UPDATE requests
        SET status = 'denied',
            reviewed_at = CURRENT_TIMESTAMP,
            reviewed_by = ?
        WHERE id = ?
    """, (admin_id, request_id))
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.admin_dashboard"))

@requests_bp.post("/requests", endpoint="create")
@jwt_required()
def create_request():
    user_id = int(get_jwt_identity())
    data = request.form

    request_type = data.get("type")
    description = data.get("description")

    if not request_type or not description:
        abort(400, "Missing required fields")

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

    # Insert request
    cursor.execute(
        """
        INSERT INTO requests (user_id, type, description, status, created_at)
        VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)
        """,
        (user_id, request_type, description)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard.user_dashboard"))

