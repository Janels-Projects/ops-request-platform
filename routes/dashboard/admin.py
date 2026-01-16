from flask import render_template, jsonify, redirect, url_for, abort, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import dashboard_bp
from routes.auth import admin_required
from models.db import get_db_connection
from rules.request_rules import VALID_CATEGORIES
from routes.dashboard.user import _get_user_and_role




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

    # Updated to use centralized category list
    categories = sorted(VALID_CATEGORIES)

    return render_template(
        "admin_dashboard.html",
        user=user,
        labels=labels,
        categories=categories,   
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
# Admin Integrations GET route
@dashboard_bp.get("/admin/integrations")
@jwt_required()
@admin_required
def admin_integrations():
    admin_id = int(get_jwt_identity())
    admin = _get_user_and_role(admin_id)

    stats = {
        "active_integrations": 1,
        "pending_configs": 3,
        "api_calls_today": 0,
        "monthly_cost": "0.00"
    }

    integrations = {
        "azure_blob": {"connected": False},
        "azure_keyvault": {"connected": False},
        "azure_monitor": {"connected": False},
        "azure_ad": {
            "active_users": 0,
            "logins_today": 0,
            "tenant_id": "example-tenant"
        },
        "teams": {"connected": False}
    }

    recent_activity = []  # empty list is fine

    return render_template(
        "admin_integrations.html",
        user=admin,
        active_page="integrations",
        stats=stats,
        integrations=integrations,
        recent_activity=recent_activity
    )


#- - - - - - - - - - - - - - - - -
# Admin Requests GET route
@dashboard_bp.get("/dashboard/admin/requests")
@jwt_required()
@admin_required
def admin_requests():
    admin_id = int(get_jwt_identity())
    admin = _get_user_and_role(admin_id)

    conn = get_db_connection()
    requests = conn.execute("""
        SELECT *
        FROM requests
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()

    categories = sorted(VALID_CATEGORIES)

    return render_template(
        "admin_requests.html",
        user=admin,
        requests=requests,
        categories=categories
    )

# - - - - - - - - - - - - - - 
# Admin Requests POST route:
@dashboard_bp.post("/dashboard/admin/requests/go-to-dashboard")
@jwt_required()
@admin_required
def go_to_dashboard_from_requests():
    request_id = request.form.get("request_id")

    # Optional: pass request_id as a query param for future highlighting
    if request_id:
        return redirect(url_for("dashboard.admin_dashboard", focus=request_id))

    return redirect(url_for("dashboard.admin_dashboard"))


# Admin Get Route Users
@dashboard_bp.get("/dashboard/admin/users")
@jwt_required()
@admin_required
def admin_users():
    admin_id = int(get_jwt_identity())
    admin = _get_user_and_role(admin_id)

    conn = get_db_connection()
    users = conn.execute("""
        SELECT id, email, role, created_at
        FROM users
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()

    return render_template(
        "admin_users.html",
        user=admin,
        users=users
    )
