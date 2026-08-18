"""Password hashing and opaque token helpers. Never log secrets."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Optional

import bcrypt

from app.core.config import settings

_BCRYPT_MAX_BYTES: int = 72


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_password(password: str) -> str:
    raw: bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    hashed: bytes = bcrypt.hashpw(raw, bcrypt.gensalt(rounds=12))
    return hashed.decode("ascii")


def verify_password(password: str, password_hash: str) -> bool:
    raw: bytes = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    try:
        return bcrypt.checkpw(raw, password_hash.encode("ascii"))
    except ValueError:
        return False


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    pepper: str = settings.auth_secret_key
    digest: bytes = hmac.new(pepper.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).digest()
    return digest.hex()


def tokens_match(token: str, token_hash: str) -> bool:
    expected: Optional[str] = token_hash
    if not expected:
        return False
    return hmac.compare_digest(hash_token(token), expected)
