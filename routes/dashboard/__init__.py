from flask import Blueprint

dashboard_bp = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)

from . import admin
from . import user