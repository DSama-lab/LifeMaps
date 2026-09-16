import time
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends, HTTPException, Request, status
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy.orm import Session

from . import config
from .db import get_db
from .models import User

_argon = PasswordHasher()
_session = URLSafeTimedSerializer(config.SESSION_SECRET, salt="lifemaps-session")
_reset = URLSafeTimedSerializer(config.RESET_TOKEN_SECRET, salt="lifemaps-pwreset")


def hash_password(password: str) -> str:
    return _argon.hash(password)


def verify_password(password: str, password_hash: Optional[str]) -> bool:
    if not password_hash:
        return False
    try:
        return _argon.verify(password_hash, password)
    except VerifyMismatchError:
        return False
    except Exception:
        return False


def sign_user_id(user_id: int) -> str:
    return _session.dumps(str(user_id))


def verify_session(token: str, max_age: int | None = None) -> Optional[int]:
    try:
        payload = _session.loads(token, max_age=max_age or config.SESSION_MAX_AGE)
        return int(payload)
    except (BadSignature, ValueError):
        return None


def sign_reset_token(user_id: int, email: str) -> str:
    return _reset.dumps(f"{user_id}:{email.strip().lower()}")


def verify_reset_token(token: str, email: str, max_age: int) -> Optional[int]:
    try:
        payload = _reset.loads(token, max_age=max_age)
    except Exception:
        return None
    parts = payload.split(":", 1)
    if len(parts) != 2 or parts[1].strip().lower() != email.strip().lower():
        return None
    try:
        return int(parts[0])
    except ValueError:
        return None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(config.SESSION_COOKIE)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Não autenticado")
    user_id = verify_session(token)
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sessão inválida ou expirada")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário não encontrado")
    return user


class RateLimiter:
    def __init__(self, key: str, limit_per_min: int):
        self._key = key
        self._limit = limit_per_min
        self._buckets: dict[str, list[float]] = {}

    def allow(self, client_key: str) -> bool:
        now = time.monotonic()
        window_start = now - 60
        hits = [t for t in self._buckets.get(client_key, []) if t > window_start]
        if len(hits) >= self._limit:
            self._buckets[client_key] = hits
            return False
        hits.append(now)
        self._buckets[client_key] = hits
        return True


_login_limiter = RateLimiter("login", config.RATE_LOGIN_PER_MIN)
_doc_limiter = RateLimiter("doc_put", config.RATE_DOC_PUT_PER_MIN)


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_login_rate(request: Request) -> None:
    if not _login_limiter.allow(client_ip(request)):
        raise HTTPException(429, "Muitas tentativas de login. Tente novamente em 1 minuto.")


def enforce_doc_rate(request: Request) -> None:
    if not _doc_limiter.allow(client_ip(request)):
        raise HTTPException(429, "Muitas gravações. Tente novamente em 1 minuto.")