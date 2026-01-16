from flask import render_template, redirect, url_for, jsonify, abort, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import dashboard_bp
from models.db import get_db_connection
from rules.request_rules import VALID_CATEGORIES
from flask import render_template, abort
import markdown




# User helper
def _get_user_and_role(user_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, email, role FROM users WHERE id = ?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user


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
        active_page="dashboard",
        **data
    )

# - - - - - - - - - - - - - -
# User Profile Route
@dashboard_bp.get("/user/profile")
@jwt_required()
def user_profile():
    user_id = int(get_jwt_identity())

    # Fetch user basic info
    user = _get_user_and_role(user_id)
    if not user:
        return jsonify({"error": "user not found"}), 404

    conn = get_db_connection()
    cur = conn.cursor()

    # Personal request stats (derived, not stored)
    cur.execute("""
        SELECT
            COUNT(*) AS total_requests,
            AVG(
                CASE
                    WHEN status = 'completed'
                    THEN julianday(reviewed_at) - julianday(created_at)
                    ELSE NULL
                END
            ) AS avg_completion_days
        FROM requests
        WHERE user_id = ?
    """, (user_id,))
    stats = cur.fetchone()

    # Most common category
    cur.execute("""
        SELECT category
        FROM requests
        WHERE user_id = ?
        GROUP BY category
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """, (user_id,))
    most_common = cur.fetchone()

    conn.close()

    return render_template(
        "user_profile.html",
        user=user,
        stats={
            "total_requests": stats["total_requests"],
            "avg_completion_days": stats["avg_completion_days"],
            "most_common_category": most_common["category"] if most_common else None,
        },
        active_page="profile"
    )



# User Setting (Preferences) Route
@dashboard_bp.get("/user/settings")
@jwt_required()
def user_preferences():
    user_id = int(get_jwt_identity())
    user = _get_user_and_role(user_id)

    conn = get_db_connection()
    cur = conn.cursor()

    # Fetch preferences
    cur.execute(
        "SELECT * FROM user_preferences WHERE user_id = ?",
        (user_id,)
    )
    prefs = cur.fetchone()

    # Lazy-create defaults if missing
    if not prefs:
        cur.execute(
            "INSERT INTO user_preferences (user_id) VALUES (?)",
            (user_id,)
        )
        conn.commit()
        cur.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?",
            (user_id,)
        )
        prefs = cur.fetchone()

    conn.close()

    return render_template(
        "user_settings.html",
        user=user,
        prefs=prefs,
        active_page="settings"
    )



# User Settings (preference) POST Route:
@dashboard_bp.post("/user/settings")
@jwt_required()
def update_user_preferences():
    user_id = int(get_jwt_identity())
    
    # Get form data
    email_on_approval = 1 if request.form.get("email_on_approval") else 0
    email_on_denial = 1 if request.form.get("email_on_denial") else 0
    email_on_status_change = 1 if request.form.get("email_on_status_change") else 0
    email_on_comment = 1 if request.form.get("email_on_comment") else 0
    daily_digest = 1 if request.form.get("daily_digest") else 0
    theme = request.form.get("theme", "light")
    requests_per_page = int(request.form.get("requests_per_page", 25))
    default_view = request.form.get("default_view", "list")
    default_department = request.form.get("default_department") or None
    default_priority = request.form.get("default_priority", "medium")
    timezone = request.form.get("timezone", "America/New_York")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        """
        UPDATE user_preferences 
        SET email_on_approval = ?,
            email_on_denial = ?,
            email_on_status_change = ?,
            email_on_comment = ?,
            daily_digest = ?,
            theme = ?,
            requests_per_page = ?,
            default_view = ?,
            default_department = ?,
            default_priority = ?,
            timezone = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
        """,
        (
            email_on_approval,
            email_on_denial,
            email_on_status_change,
            email_on_comment,
            daily_digest,
            theme,
            requests_per_page,
            default_view,
            default_department,
            default_priority,
            timezone,
            user_id,
        ),
    )
    
    conn.commit()
    conn.close()
    
    return redirect(url_for("dashboard.user_preferences"))



# - - - - - - - - - - - - - -
# User Knowledge Base
# - - - - - - - - - - - - - -
@dashboard_bp.get("/user/knowledge-base")
@jwt_required()
def user_knowledge_base():
    user_id = int(get_jwt_identity())
    user = _get_user_and_role(user_id)

    if not user:
        return jsonify({"error": "user not found"}), 404

    return render_template(
        "user_knowledge.html",
        user=user,
        categories=VALID_CATEGORIES,
        active_page="knowledge_base"
    )

# User Knowledge base article:
@dashboard_bp.get("/dashboard/user/knowledge-base/article/<slug>")
@jwt_required()
def kb_article_detail(slug):
    import markdown

    user_id = int(get_jwt_identity())
    user = _get_user_and_role(user_id)

    db = get_db_connection()
    cur = db.cursor()

    article = cur.execute(
        """
        SELECT title, category, summary, content, created_at
        FROM kb_articles
        WHERE slug = ?
        """,
        (slug,)
    ).fetchone()

    if not article:
        abort(404)

    # ✅ RENDER MARKDOWN → HTML
    html_content = markdown.markdown(
        article["content"],
        extensions=["fenced_code", "tables"]
    )

    return render_template(
        "kb_article_detail.html",
        user=user,
        article=article,
        article_html=html_content,
        active_page="knowledge_base"
    )


# User Integrations GET Route
@dashboard_bp.get("/integrations")
@jwt_required()
def user_integrations():
    user_id = int(get_jwt_identity())
    user = _get_user_and_role(user_id)

    return render_template(
        "integrations.html",
        user=user,
        is_admin=False,
        active_page="integrations"
    )



# - - - - - - - - - - - - - -
# API Route 
# - - - - - - - - - - - - - -
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