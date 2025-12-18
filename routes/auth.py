from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.db import get_db_connection

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.post("/login")
def login():
    data = request.get_json()
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

    access_token = create_access_token(
        identity=str(user["id"]),
        additional_claims={"role": user["role"]}
    )

    return jsonify({
        "access_token": access_token,
        "role": user["role"]
    }), 200


@auth_bp.get("/me")
@jwt_required()
def get_me():
    user_id = get_jwt_identity()

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
