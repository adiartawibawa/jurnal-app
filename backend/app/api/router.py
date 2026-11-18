from fastapi import APIRouter

from backend.app.api.routes import login
from backend.app.api.routes import health, users

# Router induk: semua router fitur didaftarkan di sini
api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(login.router)
api_router.include_router(users.router)