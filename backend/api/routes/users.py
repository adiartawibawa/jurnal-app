import uuid

from fastapi import APIRouter, HTTPException, status

from api.deps import CurrentUser, SessionDep
from crud import user as crud_user
from models.models import User
from schemas.user import UserPublic, UserRegister

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(session: SessionDep, user_in: UserRegister) -> User:
    """Mendaftarkan user baru; ditolak (409) jika email sudah dipakai."""
    if crud_user.get_user_by_email(session=session, email=user_in.email):
        raise HTTPException(status_code=409, detail="Email sudah terdaftar")
    return crud_user.create_user(session=session, user_in=user_in)

@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> User:
    """Mengembalikan data user yang sedang login."""
    return current_user

@router.get("/{user_id}", response_model=UserPublic)
def read_user(session: SessionDep, user_id: uuid.UUID) -> User:
    """Mengambil satu user berdasarkan id; 404 jika tidak ditemukan."""
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return user