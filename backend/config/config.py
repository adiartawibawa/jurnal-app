import warnings
from typing import Literal
from pydantic import (
    PostgresDsn,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_ignore_empty=True,
        extra="ignore"
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FASTAPI_ENV: Literal["development"] | None = None

    PROJECT_NAME: str
    DATABASE_URL: PostgresDsn

    # Reset password
    RESET_TOKEN_EXPIRE_MINUTES: int = 15
    FRONTEND_URL: str = "http://localhost:3000"

    # Email (SMTP). Kosongkan SMTP_HOST untuk mode development:
    # isi email akan dicetak ke log, bukan dikirim.
    SMTP_HOST: str | None = None
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = "no-reply@example.com"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def _use_psycopg_driver(cls, value: str | PostgresDsn) -> str:
        database_url = str(value)
        for scheme in ("postgres://", "postgresql://"):
            if database_url.startswith(scheme):
                return database_url.replace(scheme, "postgresql+psycopg://", 1)
        return database_url

        
settings = Settings()  # type: ignore[call-arg]  # nilai dibaca dari .env