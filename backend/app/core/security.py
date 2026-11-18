import hashlib
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from backend.app.core.config import settings

# Algoritma penandatanganan token JWT
ALGORITHM = "HS256"

# Hasher dengan algoritma yang direkomendasikan (Argon2)
password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """Mengubah password asli menjadi hash yang aman disimpan di database."""
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Mencocokkan password asli dengan hash yang tersimpan."""
    return password_hash.verify(plain_password, hashed_password)


def password_fingerprint(hashed_password: str) -> str:
    """Sidik jari singkat dari hash password.

    Nilainya berubah setiap password diganti, sehingga semua token lama
    (login maupun reset) otomatis tidak berlaku lagi.
    """
    return hashlib.sha256(hashed_password.encode()).hexdigest()[:16]


def _create_token(
    *, subject: str, pwd_fingerprint: str, purpose: str, expires_delta: timedelta
) -> str:
    """Membuat JWT. `purpose` mencegah token reset dipakai sebagai token login."""
    payload = {
        "sub": subject,
        "exp": datetime.now(UTC) + expires_delta,
        "purpose": purpose,
        "pwd": pwd_fingerprint,
        "jti": uuid.uuid4().hex,  # id unik token, dipakai untuk logout
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(*, subject: str, pwd_fingerprint: str) -> str:
    """Token login (berlaku ACCESS_TOKEN_EXPIRE_MINUTES)."""
    return _create_token(
        subject=subject,
        pwd_fingerprint=pwd_fingerprint,
        purpose="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_password_reset_token(*, subject: str, pwd_fingerprint: str) -> str:
    """Token reset password (berlaku RESET_TOKEN_EXPIRE_MINUTES, singkat)."""
    return _create_token(
        subject=subject,
        pwd_fingerprint=pwd_fingerprint,
        purpose="reset",
        expires_delta=timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str, *, purpose: str) -> dict[str, Any]:
    """Memverifikasi tanda tangan, masa berlaku, dan jenis token.

    Melempar jwt.InvalidTokenError jika ada yang tidak sesuai.
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"require": ["exp", "sub"]},
    )
    if payload.get("purpose") != purpose:
        raise jwt.InvalidTokenError("Jenis token tidak sesuai")
    return payload