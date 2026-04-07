import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///auth.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_MAX_AGE_SECONDS = int(os.environ.get("TOKEN_MAX_AGE_SECONDS", "3600"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
