from flask import Blueprint

requests_bp = Blueprint("requests", __name__, url_prefix="/dashboard")

from . import user
from . import admin
