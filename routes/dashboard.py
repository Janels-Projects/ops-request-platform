# routes/dashboard.py
from flask import Blueprint, render_template, redirect, url_for, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import get_db_connection  # adjust if your import path differs
from routes.auth import admin_required



dashboard_bp = Blueprint("dashboard", __name__)


def _get_user_and_role(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, email, role FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user


# - - - - - - - - - - - - - - 
# Admin metrics
def _admin_metrics():
    conn = get_db_connection()
    cur = conn.cursor()

    # --- Metrics ---
    cur.execute("SELECT COUNT(*) AS c FROM requests WHERE status = 'pending'")
    pending_count = cur.fetchone()["c"]

    cur.execute("SELECT COUNT(*) AS c FROM requests WHERE DATE(created_at) = DATE('now')")
    new_today = cur.fetchone()["c"]

    # Avg approval time (approved only)
    cur.execute("""
        SELECT AVG((julianday(reviewed_at) - julianday(created_at)) * 24.0) AS avg_hours
        FROM requests
        WHERE status = 'approved' AND reviewed_at IS NOT NULL
    """)
    avg_hours = cur.fetchone()["avg_hours"]

    # --- SINGLE DATASET FOR DASHBOARD TABLE ---
    cur.execute("""
        SELECT
            r.id,
            u.email AS employee,
            r.request_type,
            r.category,
            r.priority,
            r.department,
            r.status,
            CAST((julianday('now') - julianday(r.created_at)) AS INT) AS age_days,
            r.created_at
        FROM requests r
        JOIN users u ON u.id = r.user_id
        WHERE r.status != 'cancelled'
        ORDER BY
            CASE r.status
                WHEN 'pending' THEN 1
                WHEN 'approved' THEN 2
                WHEN 'in_progress' THEN 3
                WHEN 'completed' THEN 4
                WHEN 'denied' THEN 5
                ELSE 6
            END,
            r.created_at DESC
        LIMIT 50
    """)
    requests = cur.fetchall()

    # --- Insight (still based on pending only) ---
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

    if slowest and slowest["category"] and slowest["avg_pending_days"] is not None:
        insight = f"{slowest['category']} requests are waiting the longest on average right now."
    else:
        insight = "Queue looks healthy. No category is significantly delayed."

    return {
        "pending_count": pending_count,
        "new_today": new_today,
        "avg_hours": avg_hours,
        "requests": requests,     # 👈 unified dataset
        "insight": insight
    }


# - - - - - - - - - - - - - - 
# User Metrics 
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


# - - - - - - - - - - - - - - 
# Admin Dashboard
@dashboard_bp.get("/dashboard/admin")
@jwt_required()
def admin_dashboard():
    user_id = get_jwt_identity()
    user = _get_user_and_role(int(user_id))
    if not user or user["role"] != "admin":
        abort(403) 

    data = _admin_metrics()

    # Theme-ready labels (corporate base). Later you can swap by org theme.
    labels = {
        "title": "Corporate Operations Dashboard",
        "pending": "Pending Requests",
        "avg": "Avg Approval Time",
        "new_today": "New Requests Today"
    }

    # 👇 ADD THIS
    categories = ["Access", "Hardware", "Software"]

    return render_template(
        "admin_dashboard.html",
        user=user,
        labels=labels,
        categories=categories,   # 👈 ADD THIS
        **data
    )


# - - - - - - - - - - - - - - 
#Admin Setting's GET Route (POST route on admin_settings.py file)
@dashboard_bp.get("/dashboard/admin/settings")
@jwt_required()
@admin_required
def admin_settings_page():
    user_id = get_jwt_identity()
    user = _get_user_and_role(int(user_id))

    return render_template(
        "admin_settings.html",
        user=user
    )

# - - - - - - - - - - - - - - 
# Admin analytics GET route 
@dashboard_bp.get("/dashboard/admin/analytics")
@jwt_required()
@admin_required
def admin_analytics():
    user_id = get_jwt_identity()
    user = _get_user_and_role(int(user_id))

    # Stub metrics so the page loads
    metrics = {
        "total_requests": 0,
        "pending_requests": 0,
        "completed_requests": 0,
    }

    return render_template(
        "admin_analytics.html",
        user=user,
        metrics=metrics
    )


# - - - - - - - - - - - - - - 
# Admin anlalytics POST route
@dashboard_bp.post("/dashboard/admin/analytics")
@jwt_required()
@admin_required
def admin_analytics_post():
    # Later: read form data (date range, category, department)
    # For now, just reload page
    return redirect(url_for("dashboard.admin_analytics"))


# - - - - - - - - - - - - - - 
# User Dashboard 
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


@dashboard_bp.get("/api/user/requests")
@jwt_required()
def user_requests_api():
    user_id = get_jwt_identity()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            request_type,
            category,
            department,
            priority,
            status,
            created_at,
            reviewed_at,
            admin_review_notes
        FROM requests
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (int(user_id),))

    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {
            "id": row["id"],
            "request_type": row["request_type"],
            "category": row["category"],
            "department": row["department"],
            "priority": row["priority"],
            "status": row["status"],
            "created_at": row["created_at"],
            "reviewed_at": row["reviewed_at"],
            "admin_review_notes": row["admin_review_notes"],
        }
        for row in rows
    ])

