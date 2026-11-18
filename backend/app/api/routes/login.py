import uuid
from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.api.deps import CurrentUser, SessionDep, TokenPayloadDep
from backend.app.core.mailer import send_reset_password_email
from backend.app.core.security import (
    create_access_token,
    create_password_reset_token,
    decode_token,
    password_fingerprint,
)
from crud import token as crud_token
from crud import user as crud_user
from backend.app.models.user import User
from schemas.auth import ForgotPasswordRequest, Message, ResetPasswordRequest
from schemas.token import Token

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Login dengan form (username diisi email); mengembalikan token JWT."""
    user = crud_user.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if user is None or not user.is_active:
        raise HTTPException(status_code=400, detail="Email atau password salah")
    token = create_access_token(
        subject=str(user.id), pwd_fingerprint=password_fingerprint(user.hashed_password)
    )
    return Token(access_token=token)


@router.post("/logout")
def logout(
    session: SessionDep, _: CurrentUser, payload: TokenPayloadDep
) -> Message:
    """Logout: token yang sedang dipakai dicabut dan tidak bisa dipakai lagi."""
    crud_token.revoke_token(
        session=session,
        jti=payload["jti"],
        expires_at=datetime.fromtimestamp(payload["exp"], UTC),
    )
    return Message(message="Berhasil logout")


@router.post("/forgot-password")
def forgot_password(
    session: SessionDep,
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
) -> Message:
    """Meminta tautan reset password lewat email.

    Responsnya selalu sama, terdaftar atau tidak, agar orang lain tidak bisa
    menebak email mana yang punya akun.
    """
    user = crud_user.get_user_by_email(session=session, email=body.email)
    if user is not None and user.is_active:
        token = create_password_reset_token(
            subject=str(user.id), pwd_fingerprint=password_fingerprint(user.hashed_password)
        )
        # Dikirim di latar belakang agar waktu respons tidak membocorkan apa pun
        background_tasks.add_task(send_reset_password_email, to=user.email, token=token)
    return Message(message="Jika email terdaftar, tautan reset password telah dikirim")


@router.post("/reset-password")
def reset_password(session: SessionDep, body: ResetPasswordRequest) -> Message:
    """Membuat password baru memakai token dari email (sekali pakai)."""
    invalid = HTTPException(status_code=400, detail="Token tidak valid atau sudah kedaluwarsa")
    try:
        payload = decode_token(body.token, purpose="reset")
        user_id = uuid.UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError, TypeError):
        raise invalid

    user = session.get(User, user_id)
    # Sidik jari berbeda = password sudah pernah diganti = token sudah terpakai
    if (
        user is None
        or not user.is_active
        or payload.get("pwd") != password_fingerprint(user.hashed_password)
    ):
        raise invalid

    crud_user.update_password(session=session, user=user, new_password=body.new_password)
    return Message(message="Password berhasil diubah")