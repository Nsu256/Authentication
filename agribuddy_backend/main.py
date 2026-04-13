from flask import Flask
from flask_cors import CORS
from auth_routes import auth_bp
from config import Config
from extensions import db
from seed import seed_default_users

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
db.init_app(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()
    seed_default_users(app)


@app.route("/", methods=["GET"])
def home():
    return {"message": "Agribuddy Authentication API is running"}, 200


@app.route("/api/docs", methods=["GET"])
def api_docs():
    return {
        "message": "Available API endpoints",
        "endpoints": [
            {
                "method": "GET",
                "path": "/",
                "description": "API health endpoint",
                "auth": "No",
            },
            {
                "method": "GET",
                "path": "/api/docs",
                "description": "List all available endpoints",
                "auth": "No",
            },
            {
                "method": "POST",
                "path": "/api/login",
                "description": "Login for administrator or farmer",
                "auth": "No",
            },
            {
                "method": "POST",
                "path": "/api/register",
                "description": "Register a farmer account",
                "auth": "No",
            },
            {
                "method": "GET",
                "path": "/api/me",
                "description": "Get current token payload",
                "auth": "Bearer token",
            },
            {
                "method": "GET",
                "path": "/api/admin/users",
                "description": "List all users (admin only)",
                "auth": "Bearer token (administrator)",
            },
            {
                "method": "POST",
                "path": "/api/admin/users",
                "description": "Create farmer user (admin only)",
                "auth": "Bearer token (administrator)",
            },
            {
                "method": "GET",
                "path": "/api/farmer/profile",
                "description": "Get farmer profile (farmer only)",
                "auth": "Bearer token (farmer)",
            },
        ],
    }, 200


if __name__ == "__main__":
    app.run(debug=True)