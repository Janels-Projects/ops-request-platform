# User profile routes with role-based and ownership-based access control

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.db import get_db_connection
from flask import request
from utils.ownership import enforce_owner_or_admin



users_bp = Blueprint("users", __name__, url_prefix="/users")

# Get route
@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    # Authorization check
    if role != "admin" and current_user_id != user_id:
        return jsonify({"error": "access denied"}), 403

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


# Allow access only to the resource owner or admins (PUT route)
@users_bp.put("/<int:user_id>")
@jwt_required()
def update_user(user_id):
    denied = enforce_owner_or_admin(user_id)
    if denied:
        return denied

    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "email is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET email = ? WHERE id = ?",
        (email, user_id)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "user updated"}), 200


# DELETE route 
@users_bp.delete("/<int:user_id>")
@jwt_required()
def delete_user(user_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    # Ownership / admin check
    if role != "admin" and current_user_id != user_id:
        return jsonify({"error": "access denied"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "user deleted"}), 200
