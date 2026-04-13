import os


def _env_to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///auth.db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_MAX_AGE_SECONDS = int(os.environ.get("TOKEN_MAX_AGE_SECONDS", "3600"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    ENABLE_ADMIN_SEED = _env_to_bool(os.environ.get("ENABLE_ADMIN_SEED"), False)
    DEFAULT_ADMIN_EMAIL = os.environ.get("DEFAULT_ADMIN_EMAIL", "admin@agribuddy.com")
    DEFAULT_ADMIN_PASSWORD = os.environ.get("DEFAULT_ADMIN_PASSWORD", "Admin@123")
