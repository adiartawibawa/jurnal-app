from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.core.config import settings

# Instance aplikasi utama (dinamai `app` agar dikenali fastapi dev / uvicorn)
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Semua endpoint diawali /api/v1 (diambil dari settings.API_V1_STR)
app.include_router(api_router, prefix=settings.API_V1_STR)