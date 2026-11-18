from sqlmodel import Session, select

from config.security import get_password_hash, verify_password
from models.models import User
from schemas.user import UserRegister


# Hash palsu untuk menyamakan waktu proses saat email tidak ditemukan,
# agar penyerang tidak bisa menebak email terdaftar dari kecepatan respons.
DUMMY_HASH = get_password_hash("fake-password")

def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Mencari user berdasarkan email; mengembalikan None jika tidak ada."""
    return session.exec(select(User).where(User.email == email)).first()


def create_user(*, session: Session, user_in: UserRegister) -> User:
    """Menyimpan user baru ke database dengan password yang sudah di-hash."""
    db_user = User.model_validate(
        user_in,
        update={"hashed_password": get_password_hash(user_in.password)},
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Memeriksa email + password; mengembalikan user jika cocok, selain itu None."""
    user = get_user_by_email(session=session, email=email)
    if user is None:
        verify_password(password, DUMMY_HASH)
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def update_password(*, session: Session, user: User, new_password: str) -> None:
    """Mengganti password user dengan hash dari password baru."""
    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    session.commit()