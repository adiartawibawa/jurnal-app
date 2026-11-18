import uuid
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from backend.app.models.user import UserBase


class UserRegister(SQLModel):
    """Data yang dikirim klien saat mendaftar.

    Sengaja tidak memuat is_superuser/is_active agar klien tidak bisa
    menjadikan dirinya admin lewat request.
    """

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


class UserPublic(UserBase):
    """Data user yang aman dikembalikan ke klien (tanpa hashed_password)."""

    id: uuid.UUID
    created_at: datetime | None = None