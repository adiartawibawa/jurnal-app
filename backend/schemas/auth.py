from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class Message(SQLModel):
    """Respons sederhana berisi satu pesan."""

    message: str


class ForgotPasswordRequest(SQLModel):
    """Data untuk meminta tautan reset password."""

    email: EmailStr


class ResetPasswordRequest(SQLModel):
    """Data untuk membuat password baru memakai token dari email."""

    token: str
    new_password: str = Field(min_length=8, max_length=128)