print("✅ admin_settings routes loaded")

from flask import redirect, url_for, request, abort
from flask_jwt_extended import jwt_required

from routes.dashboard import dashboard_bp
from routes.auth import admin_required


# -------- Categories --------
@dashboard_bp.post("/admin/settings/categories/add")
@jwt_required()
@admin_required
def add_category():
    return redirect(url_for("dashboard.admin_settings_page"))

@dashboard_bp.post("/dashboard/admin/settings/categories/delete")
@jwt_required()
@admin_required
def delete_category():
    return redirect(url_for("dashboard.admin_settings_page"))


# -------- Departments --------
@dashboard_bp.post("/admin/settings/departments/add")
@jwt_required()
@admin_required
def add_department():
    return redirect(url_for("dashboard.admin_settings_page"))

@dashboard_bp.post("/admin/settings/departments/delete")
@jwt_required()
@admin_required
def delete_department():
    return redirect(url_for("dashboard.admin_settings_page"))


# -------- Users --------
@dashboard_bp.post("/admin/settings/users/toggle-role")
@jwt_required()
@admin_required
def toggle_user_role():
    user_id = request.form.get("user_id")
    new_role = request.form.get("new_role")

    if not user_id or not new_role:
        abort(400)

    return redirect(url_for("dashboard.admin_settings_page"))

