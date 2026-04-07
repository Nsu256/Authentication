import os
import sqlite3
from datetime import UTC, datetime

from flask import Flask, jsonify, request
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-in-production")
app.config["TOKEN_MAX_AGE_SECONDS"] = int(os.environ.get("TOKEN_MAX_AGE_SECONDS", "3600"))

CORS(app, resources={r"/api/*": {"origins": os.environ.get("CORS_ORIGINS", "*")}})

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "auth.db")
ALLOWED_ROLES = {"administrator", "farmer"}


def get_db_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_access_token(user_id: int, role: str, email: str) -> str:
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "iat": int(datetime.now(UTC).timestamp()),
    }
    return serializer.dumps(payload)


def verify_access_token(token: str) -> dict:
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    return serializer.loads(token, max_age=app.config["TOKEN_MAX_AGE_SECONDS"])


def initialize_database() -> None:
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('administrator', 'farmer'))
        )
        """
    )

    default_users = [
        ("admin@agribuddy.com", generate_password_hash("Admin@123"), "administrator"),
        ("farmer@agribuddy.com", generate_password_hash("Farmer@123"), "farmer"),
    ]

    cursor.executemany(
        """
        INSERT OR IGNORE INTO users (email, password_hash, role)
        VALUES (?, ?, ?)
        """,
        default_users,
    )

    connection.commit()
    connection.close()


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    role = str(data.get("role", "")).strip().lower()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password or not role:
        return jsonify({"error": "email, password, and role are required"}), 400

    if role not in ALLOWED_ROLES:
        return jsonify({"error": "role must be either 'administrator' or 'farmer'"}), 400

    connection = get_db_connection()
    user = connection.execute(
        "SELECT id, email, password_hash, role FROM users WHERE email = ?",
        (email,),
    ).fetchone()
    connection.close()

    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401

    if not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    if user["role"] != role:
        return jsonify({"error": "Invalid role for this account"}), 403

    access_token = create_access_token(user["id"], user["role"], user["email"])
    return (
        jsonify(
            {
                "message": "Login successful",
                "access_token": access_token,
                "user": {
                    "id": user["id"],
                    "email": user["email"],
                    "role": user["role"],
                },
            }
        ),
        200,
    )


@app.route("/api/me", methods=["GET"])
def me():
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_access_token(token)
    except SignatureExpired:
        return jsonify({"error": "Token has expired"}), 401
    except BadSignature:
        return jsonify({"error": "Invalid token"}), 401

    return jsonify({"user": payload}), 200


initialize_database()


if __name__ == "__main__":
    app.run(debug=True)