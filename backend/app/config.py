import os


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


DATABASE_URL = env("DATABASE_URL")
SESSION_SECRET = env("SESSION_SECRET")
RESET_TOKEN_SECRET = env("RESET_TOKEN_SECRET", SESSION_SECRET)
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET")
CORS_ORIGINS = [o.strip() for o in env("CORS_ORIGINS", "").split(",") if o.strip()]
DOC_MAX_BYTES = int_env("DOC_MAX_BYTES", 5_242_880)
RATE_LOGIN_PER_MIN = int_env("RATE_LOGIN_PER_MIN", 10)
RATE_DOC_PUT_PER_MIN = int_env("RATE_DOC_PUT_PER_MIN", 60)
SESSION_COOKIE = "lifemaps_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 30
APP_ENV = env("APP_ENV", "production")
PASSWORD_RESET_MAX_AGE = int_env("PASSWORD_RESET_MAX_AGE", 30 * 60)