from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..crypto import decrypt_secret, encrypt_secret
from ..db import get_db
from ..models import User, UserSettings
from ..schemas import SettingsIn, SettingsOut
from ..security import get_current_user

router = APIRouter(prefix="/api", tags=["settings"])


def _row(db: Session, user_id: int) -> UserSettings:
    row = db.get(UserSettings, user_id)
    if row is None:
        row = UserSettings(user_id=user_id, data={})
        db.add(row)
        db.flush()
    return row


def _to_out(row: UserSettings) -> SettingsOut:
    data = row.data or {}
    return SettingsOut(
        provider=str(data.get("provider", "") or ""),
        model=str(data.get("model", "") or ""),
        ai_key=decrypt_secret(str(data.get("ai_key", "") or "")),
    )


@router.get("/settings", response_model=SettingsOut)
def get_settings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _row(db, user.id)
    db.commit()
    return _to_out(_row(db, user.id))


@router.put("/settings", response_model=SettingsOut)
def put_settings(
    body: SettingsIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    row = _row(db, user.id)
    data = dict(row.data or {})
    if body.provider is not None:
        data["provider"] = (body.provider or "groq")[:40]
    if body.model is not None:
        data["model"] = (body.model or "")[:160]
    if body.ai_key is not None:
        data["ai_key"] = encrypt_secret(body.ai_key or "")
    row.data = data
    db.commit()
    db.refresh(row)
    return _to_out(row)