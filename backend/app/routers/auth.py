import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from google.oauth2 import id_token as google_id_token
from google.auth.transport.requests import Request as GoogleRequest
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config
from ..db import get_db
from ..models import User
from ..schemas import (
    ForgotPasswordIn,
    GoogleLoginIn,
    PasswordLoginIn,
    RegisterIn,
    ResetPasswordIn,
    UserOut,
)
from ..security import (
    enforce_login_rate,
    get_current_user,
    hash_password,
    sign_reset_token,
    sign_user_id,
    verify_password,
    verify_reset_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

_FAIL = "E-mail ou senha incorretos"


def _set_session(response, user_id: int) -> None:
    token = sign_user_id(user_id)
    response.set_cookie(
        config.SESSION_COOKIE,
        token,
        max_age=config.SESSION_MAX_AGE,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
    )


@router.post("/google", response_model=UserOut)
def login_google(
    body: GoogleLoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    enforce_login_rate(request)
    try:
        info = google_id_token.verify_oauth2_token(
            body.id_token, GoogleRequest(), config.GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token Google inválido")
    if not info or not info.get("email_verified"):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token Google inválido")

    sub = str(info["sub"])
    email = info["email"]
    name = info.get("name", "") or ""

    user = db.scalar(select(User).where(User.google_sub == sub))
    if user is None:
        user = db.scalar(select(User).where(User.email == email))
        if user is not None:
            user.google_sub = sub
        else:
            user = User(email=email, name=name, google_sub=sub)
            db.add(user)
        db.commit()
        db.refresh(user)
    _set_session(response, user.id)
    return user


@router.post("/register", response_model=UserOut)
def register(
    body: RegisterIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    enforce_login_rate(request)
    email = body.email.strip().lower()
    if not email or len(body.password) < 8:
        raise HTTPException(400, "E-mail inválido ou senha muito curta (mín. 8)")
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "E-mail já cadastrado")
    user = User(email=email, name=body.name, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    _set_session(response, user.id)
    return user


@router.post("/login", response_model=UserOut)
def login_password(
    body: PasswordLoginIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    enforce_login_rate(request)
    email = body.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, _FAIL)
    _set_session(response, user.id)
    return user


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(config.SESSION_COOKIE, path="/")


@router.post("/refresh", response_model=UserOut)
def refresh_session(response: Response, user: User = Depends(get_current_user)):
    _set_session(response, user.id)
    return user


@router.post("/forgot-password")
def forgot_password(
    body: ForgotPasswordIn,
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_login_rate(request)
    email = body.email.strip().lower()
    user = None
    if email:
        user = db.scalar(select(User).where(User.email == email))
    if user is None:
        return {"status": True}
    token = sign_reset_token(user.id, user.email)
    logging.info("Password reset %s -> /reset-password/%s", email, token)
    if config.APP_ENV == "dev":
        return {"status": True, "dev_token": token}
    return {"status": True}


@router.post("/reset-password", response_model=UserOut)
def reset_password(
    body: ResetPasswordIn,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    enforce_login_rate(request)
    email = body.email.strip().lower()
    if not email or len(body.password) < 8:
        raise HTTPException(400, "E-mail inválido ou senha muito curta (mín. 8)")
    user_id = verify_reset_token(body.token, email, config.PASSWORD_RESET_MAX_AGE)
    if user_id is None:
        raise HTTPException(400, "Token de redefinição inválido ou expirado")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(400, "Token de redefinição inválido ou expirado")
    user.password_hash = hash_password(body.password)
    db.commit()
    db.refresh(user)
    _set_session(response, user.id)
    return user


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user