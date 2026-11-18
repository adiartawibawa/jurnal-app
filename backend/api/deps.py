import uuid
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from config.config import settings
from config.dbase import get_session
from config.security import decode_token, password_fingerprint
from crud import token as crud_token
from models.models import User

# Dependency bersama: endpoint cukup menulis `session: SessionDep`
SessionDep = Annotated[Session, Depends(get_session)]

# Membaca token dari header "Authorization: Bearer <token>".
# tokenUrl dipakai tombol "Authorize" di halaman /docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login/access-token")
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def _unauthorized() -> HTTPException:
    """Error 401 standar untuk token yang tidak bisa diterima."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau sudah kedaluwarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_token_payload(token: TokenDep) -> dict[str, Any]:
    """Memverifikasi token login dan mengembalikan isinya; 401 jika tidak valid."""
    try:
        return decode_token(token, purpose="access")
    except jwt.InvalidTokenError:
        raise _unauthorized()


TokenPayloadDep = Annotated[dict[str, Any], Depends(get_token_payload)]


def get_current_user(session: SessionDep, payload: TokenPayloadDep) -> User:
    """Mengubah isi token menjadi user yang sedang login; 401 jika tidak berlaku."""
    try:
        user_id = uuid.UUID(payload["sub"])
        jti = payload["jti"]
    except (KeyError, ValueError, TypeError):
        raise _unauthorized()

    # Token yang sudah di-logout ditolak
    if crud_token.is_revoked(session=session, jti=jti):
        raise _unauthorized()

    user = session.get(User, user_id)
    if user is None or not user.is_active:
        raise _unauthorized()

    # Password sudah diganti sejak token dibuat -> token lama ditolak
    if payload.get("pwd") != password_fingerprint(user.hashed_password):
        raise _unauthorized()
    return user


# Pakai `current_user: CurrentUser` untuk membuat endpoint wajib login
CurrentUser = Annotated[User, Depends(get_current_user)]