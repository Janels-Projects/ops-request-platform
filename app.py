from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from routes.system import system_bp
from routes.auth import auth_bp
from routes.users import users_bp
from models.schema import init_db


app = Flask(__name__)
CORS(app)

# JWT config
app.config["JWT_SECRET_KEY"] = "dev-secret-change-later"
jwt = JWTManager(app)

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(system_bp)
app.register_blueprint(users_bp)


if __name__ == "__main__":
    app.run(debug=True)

