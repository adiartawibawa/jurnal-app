import uuid
from datetime import UTC, datetime

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import SQLModel, Field

def get_datetime_utc() -> datetime:
    return datetime.now(UTC)

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(default_factory=get_datetime_utc)

# Daftar token login yang sudah di-logout (denylist).
# Baris dengan expires_at yang sudah lewat aman dihapus karena token-nya toh sudah kedaluwarsa.
class RevokedToken(SQLModel, table=True):
    jti: str = Field(primary_key=True, max_length=64)
    expires_at: datetime = Field(sa_type=DateTime(timezone=True))