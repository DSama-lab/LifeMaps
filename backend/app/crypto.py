import base64
import hashlib
import logging

from cryptography.fernet import Fernet, InvalidToken

from . import config

_fernet = None
_EPHEMERAL = "lifemaps-ai-key-ephemeral"


def _key_bytes() -> bytes:
    secret = config.AI_KEY_ENCRYPT_SECRET or ""
    if not secret:
        logging.warning(
            "AI_KEY_ENCRYPT_SECRET not set — using ephemeral key (stored AI keys "
            "will not survive restarts); set it in .env"
        )
        material = _EPHEMERAL
    else:
        material = secret
    return base64.urlsafe_b64encode(hashlib.sha256(material.encode("utf-8")).digest())


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is None:
        _fernet = Fernet(_key_bytes())
    return _fernet


def encrypt_secret(plain: str) -> str:
    if not plain:
        return ""
    return _get_fernet().encrypt(plain.encode("utf-8")).decode("ascii")


def decrypt_secret(token: str) -> str:
    if not token:
        return ""
    try:
        return _get_fernet().decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, Exception):
        return ""