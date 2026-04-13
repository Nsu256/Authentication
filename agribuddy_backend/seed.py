from flask import Flask

from extensions import db
from models import User


def seed_default_users(app: Flask) -> None:
    default_users = [
        {"email": "farmer@agribuddy.com", "password": "Farmer@123", "role": "farmer"},
    ]

    if app.config["ENABLE_ADMIN_SEED"]:
        default_users.append(
            {
                "email": app.config["DEFAULT_ADMIN_EMAIL"],
                "password": app.config["DEFAULT_ADMIN_PASSWORD"],
                "role": "administrator",
            }
        )

    for default_user in default_users:
        existing_user = User.query.filter_by(email=default_user["email"]).first()
        if existing_user:
            continue

        user = User(email=default_user["email"], role=default_user["role"])
        user.set_password(default_user["password"])
        db.session.add(user)

    db.session.commit()