from flask import Flask
from routes.system import system_bp
from models.schema import init_db


app = Flask(__name__)

# Initialize database
init_db()

# Register blueprints
app.register_blueprint(system_bp)

if __name__ == "__main__":
    app.run(debug=True)
