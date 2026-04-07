from datetime import UTC, datetime

from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from models import User


auth_bp = Blueprint("auth", __name__)


def create_access_token(user: User) -> str:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    payload = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "iat": int(datetime.now(UTC).timestamp()),
    }
    return serializer.dumps(payload)


def verify_access_token(token: str) -> dict:
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.loads(token, max_age=current_app.config["TOKEN_MAX_AGE_SECONDS"])


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    role = str(data.get("role", "")).strip().lower()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password or not role:
        return jsonify({"error": "email, password, and role are required"}), 400

    if role not in User.ALLOWED_ROLES:
        return jsonify({"error": "role must be either 'administrator' or 'farmer'"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if user.role != role:
        return jsonify({"error": "Invalid role for this account"}), 403

    access_token = create_access_token(user)
    return (
        jsonify(
            {
                "message": "Login successful",
                "access_token": access_token,
                "user": user.to_dict(),
            }
        ),
        200,
    )


@auth_bp.route("/api/me", methods=["GET"])
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
