from fastapi import APIRouter
from sqlmodel import text

from backend.app.api.deps import SessionDep

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(session: SessionDep) -> dict[str, str]:
    """Memastikan aplikasi bisa menjalankan query ke database."""
    session.connection().execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}