from flask_jwt_extended import JWTManager
from flask import render_template
import os
from flask import Flask
from flask_cors import CORS
from models.seed_admin import seed_admin
from models.seed_user import seed_user


from routes.auth import auth_bp
from routes.system import system_bp
from routes.dashboard import dashboard_bp
from routes.users import users_bp
from routes.requests import requests_bp
from models.schema import init_db
from models.db import ensure_request_columns
import routes.admin_settings
from models.seed_kb_articles import seed_kb_articles




app = Flask(__name__)
CORS(app)


# Context processor
@app.context_processor
def inject_user_prefs():
    from flask_jwt_extended import get_jwt_identity
    from models.db import get_db_connection

    try:
        user_id = get_jwt_identity()
        if not user_id:
            return {}

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?",
            (int(user_id),)
        )
        prefs = cur.fetchone()
        conn.close()

        return {"prefs": prefs}
    except Exception:
        return {}


# JWT config
app.config["JWT_SECRET_KEY"] = "dev-secret-change-later"
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_ACCESS_COOKIE_NAME"] = "access_token"
app.config["JWT_ACCESS_COOKIE_PATH"] = "/"

app.config["JWT_COOKIE_SECURE"] = True          # True in HTTPS prod
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False 
  


jwt = JWTManager(app)

# - - - - - - - - - - - -  -
# Initialize database
# - - - - - - - - - - - -  -
with app.app_context():
    init_db()
    ensure_request_columns()
    seed_admin()
    seed_user()
    seed_kb_articles()



# - - - - - - - - - - - -  -
# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(system_bp)
app.register_blueprint(users_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(requests_bp) #added 1/1 to fix the above line (duplicated)

# - - - - - - - - - - - -  -
# Page Routes 
# - - - - - - - - - - - -  -
@app.get("/login")
def login_page():
    return render_template("login.html")


# - - - - - - - - - - - -  -
# Global Error Handlder 
# - - - - - - - - - - - -  -
@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


# - - - - - - - - - - - -  -
# Run / Main Guard 
# - - - - - - - - - - - -  -
if __name__ == "__main__":
    app.run(debug=True)

