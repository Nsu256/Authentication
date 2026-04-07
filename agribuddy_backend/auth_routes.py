from datetime import UTC, datetime
from functools import wraps

from flask import Blueprint, current_app, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from extensions import db
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


def get_token_payload():
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return None, (jsonify({"error": "Missing or invalid Authorization header"}), 401)

    token = authorization.split(" ", 1)[1]
    try:
        payload = verify_access_token(token)
    except SignatureExpired:
        return None, (jsonify({"error": "Token has expired"}), 401)
    except BadSignature:
        return None, (jsonify({"error": "Invalid token"}), 401)

    return payload, None


def require_role(required_role: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload, error_response = get_token_payload()
            if error_response is not None:
                return error_response

            if payload.get("role") != required_role:
                return jsonify({"error": f"{required_role} access required"}), 403

            return func(payload, *args, **kwargs)

        return wrapper

    return decorator


@auth_bp.route("/api/register", methods=["POST"])
def register_farmer():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "A user with this email already exists"}), 409

    user = User(email=email, role="farmer")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registration successful", "user": user.to_dict()}), 201


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
    payload, error_response = get_token_payload()
    if error_response is not None:
        return error_response

    return jsonify({"user": payload}), 200


@auth_bp.route("/api/admin/users", methods=["GET"])
@require_role("administrator")
def list_users(admin_payload: dict):
    users = User.query.order_by(User.id.asc()).all()
    return (
        jsonify(
            {
                "requested_by": {
                    "id": admin_payload.get("sub"),
                    "email": admin_payload.get("email"),
                    "role": admin_payload.get("role"),
                },
                "users": [user.to_dict() for user in users],
            }
        ),
        200,
    )


@auth_bp.route("/api/admin/users", methods=["POST"])
@require_role("administrator")
def create_user(admin_payload: dict):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    role = str(data.get("role", "")).strip().lower()

    if not email or not password or not role:
        return jsonify({"error": "email, password, and role are required"}), 400

    if role not in User.ALLOWED_ROLES:
        return jsonify({"error": "role must be either 'administrator' or 'farmer'"}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "A user with this email already exists"}), 409

    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {
                "message": "User created successfully",
                "created_by": {
                    "id": admin_payload.get("sub"),
                    "email": admin_payload.get("email"),
                    "role": admin_payload.get("role"),
                },
                "user": user.to_dict(),
            }
        ),
        201,
    )


@auth_bp.route("/api/farmer/profile", methods=["GET"])
@require_role("farmer")
def farmer_profile(farmer_payload: dict):
    user = User.query.get(farmer_payload.get("sub"))
    if user is None:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"profile": user.to_dict()}), 200
