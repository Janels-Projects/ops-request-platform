from flask import Blueprint, request, jsonify, redirect, make_response, abort, url_for
from werkzeug.security import check_password_hash
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    jwt_required,
    get_jwt_identity,
    unset_jwt_cookies
)
from functools import wraps
from models.db import get_db_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------------------------
# Login
# ---------------------------
@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password required"}), 400

    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, email, password, role FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "invalid credentials"}), 401

    # ✅ Create JWT with role included
    access_token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user["role"]}
    )

    # ✅ Role-aware redirect (THIS FIXES YOUR ISSUE)
    if user["role"] == "admin":
        resp = make_response(redirect(url_for("dashboard.admin_dashboard")))
    else:
        resp = make_response(redirect(url_for("dashboard.user_dashboard")))

    # ✅ Always set cookies for both roles
    set_access_cookies(resp, access_token)
    return resp


# ---------------------------
# Current User
# ---------------------------
@auth_bp.get("/me")
@jwt_required()
def get_me():
    user_id = int(get_jwt_identity())

    conn = get_db_connection()
    user = conn.execute(
        "SELECT id, email, role, created_at FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "user not found"}), 404

    return jsonify({
        "id": user["id"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"]
    }), 200


# ---------------------------
# Logout
# ---------------------------
@auth_bp.post("/logout")
def logout():
    resp = make_response(redirect("/login"))
    unset_jwt_cookies(resp)
    return resp


# ---------------------------
# Admin Guard
# ---------------------------
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()

        if not user_id:
            abort(401)

        conn = get_db_connection()
        user = conn.execute(
            "SELECT role FROM users WHERE id = ?",
            (int(user_id),)
        ).fetchone()
        conn.close()

        if not user or user["role"] != "admin":
            abort(403)

        return fn(*args, **kwargs)
    return wrapper
