from flask import jsonify
from flask_jwt_extended import get_jwt_identity, get_jwt

def enforce_owner_or_admin(resource_user_id):
    current_user_id = int(get_jwt_identity())
    role = get_jwt().get("role")

    if role != "admin" and current_user_id != resource_user_id:
        return jsonify({"error": "access denied"}), 403

    return None
