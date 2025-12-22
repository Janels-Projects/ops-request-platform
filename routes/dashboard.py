# routes/dashboard.py
from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.db import get_db_connection  # adjust if your import path differs

dashboard_bp = Blueprint("dashboard", __name__)

def _get_user_and_role(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, email, role FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def _admin_metrics():
    conn = get_db_connection()
    cur = conn.cursor()

    # Adjust table/column names if yours differ:
    # requests table assumed: id, user_id, request_type, category, status, created_at, updated_at, reviewed_at, reviewed_by
    cur.execute("SELECT COUNT(*) AS c FROM requests WHERE status = 'pending'")
    pending_count = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM requests WHERE DATE(created_at) = DATE('now')")
    new_today = cur.fetchone()["c"]

    # Avg approval time (approved only). SQLite: compute hours between created_at and reviewed_at.
    cur.execute("""
        SELECT AVG((julianday(reviewed_at) - julianday(created_at)) * 24.0) AS avg_hours
        FROM requests
        WHERE status = 'approved' AND reviewed_at IS NOT NULL
    """)
    avg_hours = cur.fetchone()["avg_hours"]

    # Pending queue
    cur.execute("""
        SELECT r.id, u.email AS employee, r.request_type, r.category, r.priority, r.status,
               CAST((julianday('now') - julianday(r.created_at)) AS INT) AS age_days,
               r.created_at
        FROM requests r
        JOIN users u ON u.id = r.user_id
        WHERE r.status = 'pending'
        ORDER BY r.created_at ASC
        LIMIT 25
    """)
    pending_requests = cur.fetchall()

    # Simple “AI-inspired” insight: find category with highest average pending age (days)
    cur.execute("""
        SELECT category,
               AVG(julianday('now') - julianday(created_at)) AS avg_pending_days
        FROM requests
        WHERE status = 'pending'
        GROUP BY category
        ORDER BY avg_pending_days DESC
        LIMIT 1
    """)
    slowest = cur.fetchone()

    conn.close()

    insight = None
    if slowest and slowest["category"] and slowest["avg_pending_days"] is not None:
        insight = f"{slowest['category']} requests are waiting the longest on average right now."
    else:
        insight = "Queue looks healthy. No category is significantly delayed."

    return {
        "pending_count": pending_count,
        "new_today": new_today,
        "avg_hours": avg_hours,
        "pending_requests": pending_requests,
        "insight": insight
    }

def _user_metrics(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM requests WHERE user_id = ? AND status IN ('pending','approved')", (user_id,))
    active_count = cur.fetchone()["c"]

    cur.execute("""
        SELECT id, request_type, category, status, created_at
        FROM requests
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 25
    """, (user_id,))
    my_requests = cur.fetchall()

    conn.close()

    return {
        "active_count": active_count,
        "my_requests": my_requests
    }

@dashboard_bp.get("/dashboard")
@jwt_required()
def dashboard_router():
    user_id = get_jwt_identity()
    user = _get_user_and_role(int(user_id))

    if not user:
        return jsonify({"error": "user not found"}), 404

    role = user["role"]
    if role == "admin":
        return redirect(url_for("dashboard.admin_dashboard"))
    return redirect(url_for("dashboard.user_dashboard"))

@dashboard_bp.get("/dashboard/admin")
@jwt_required()
def admin_dashboard():
    user_id = get_jwt_identity()
    user = _get_user_and_role(int(user_id))
    if not user or user["role"] != "admin":
        return jsonify({"error": "admin only"}), 403

    data = _admin_metrics()

    # Theme-ready labels (corporate base). Later you can swap by org theme.
    labels = {
        "title": "Corporate Operations Dashboard",
        "pending": "Pending Requests",
        "avg": "Avg Approval Time",
        "new_today": "New Requests Today"
    }

    return render_template(
        "admin_dashboard.html",
        user=user,
        labels=labels,
        **data
    )

@dashboard_bp.get("/dashboard/user")
@jwt_required()
def user_dashboard():
    user_id = get_jwt_identity()
    user = _get_user_and_role(int(user_id))
    if not user:
        return jsonify({"error": "user not found"}), 404

    data = _user_metrics(int(user_id))

    labels = {
        "title": "My Requests",
        "active": "Active Requests"
    }

    return render_template(
        "user_dashboard.html",
        user=user,
        labels=labels,
        **data
    )
