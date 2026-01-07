from flask import request, redirect, url_for, abort, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import requests_bp
from models.db import get_db_connection
from rules.request_rules import VALID_CATEGORIES, validate_transition



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