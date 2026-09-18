from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class GoogleLoginIn(BaseModel):
    id_token: str


class PasswordLoginIn(BaseModel):
    email: str
    password: str


class ForgotPasswordIn(BaseModel):
    email: str


class ResetPasswordIn(BaseModel):
    email: str
    token: str
    password: str


class RegisterIn(BaseModel):
    email: str
    password: str
    name: str = ""


class UpdateMeIn(BaseModel):
    name: str = ""


class SettingsIn(BaseModel):
    provider: Optional[str] = None
    model: Optional[str] = None
    ai_key: Optional[str] = None


class SettingsOut(BaseModel):
    provider: str = ""
    model: str = ""
    ai_key: str = ""


class UserOut(BaseModel):
    id: int
    email: str
    name: str

    model_config = {"from_attributes": True}


class DocOut(BaseModel):
    id: int
    name: str
    version: int
    data: dict

    model_config = {"from_attributes": True}


class DocMetaOut(BaseModel):
    id: int
    name: str
    version: int
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocPutIn(BaseModel):
    name: Optional[str] = None
    data: dict
    base_version: Optional[int] = None