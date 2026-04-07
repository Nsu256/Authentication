from flask import Flask
from flask_cors import CORS
from auth_routes import auth_bp
from config import Config
from extensions import db
from models import User

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})
db.init_app(app)
app.register_blueprint(auth_bp)


def seed_default_users() -> None:
    default_users = [
        {"email": "farmer@agribuddy.com", "password": "Farmer@123", "role": "farmer"},
    ]

    for default_user in default_users:
        existing_user = User.query.filter_by(email=default_user["email"]).first()
        if existing_user:
            continue

        user = User(email=default_user["email"], role=default_user["role"])
        user.set_password(default_user["password"])
        db.session.add(user)

    db.session.commit()

with app.app_context():
    db.create_all()
    seed_default_users()


if __name__ == "__main__":
    app.run(debug=True)