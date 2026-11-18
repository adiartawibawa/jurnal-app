from datetime import UTC, datetime

from sqlmodel import Session, col, delete

from models.models import RevokedToken


def is_revoked(*, session: Session, jti: str) -> bool:
    """True jika token dengan id ini sudah di-logout."""
    return session.get(RevokedToken, jti) is not None


def revoke_token(*, session: Session, jti: str, expires_at: datetime) -> None:
    """Mencatat token sebagai dicabut (logout), sekaligus membersihkan yang sudah kedaluwarsa."""
    session.exec(delete(RevokedToken).where(col(RevokedToken.expires_at) < datetime.now(UTC)))
    session.add(RevokedToken(jti=jti, expires_at=expires_at))
    session.commit()