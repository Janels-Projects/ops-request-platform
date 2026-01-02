from utils.auth import admin_required
from flask import Blueprint, jsonify

system_bp = Blueprint("system", __name__, url_prefix="/system")

@system_bp.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

@system_bp.get("/admin-check")
@admin_required
def admin_check():
    return jsonify({"status": "admin access confirmed"}), 200

# Admin route
@system_bp.get("/stats")
@admin_required
def system_stats():
    return jsonify({
        "status": "ok",
        "service": "ops-request-platform",
        "access": "admin",
        "version": "1.0.0"
    }), 200
