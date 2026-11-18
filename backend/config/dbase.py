from collections.abc import Generator

from sqlmodel import Session, create_engine

from config.config import settings

# Engine = pintu koneksi ke PostgreSQL.
# pool_pre_ping=True memeriksa koneksi lebih dulu agar tidak error karena koneksi basi.
engine = create_engine(str(settings.DATABASE_URL), pool_pre_ping=True)


def get_session() -> Generator[Session, None, None]:
    """Dependency FastAPI: membuka sesi database per request, lalu menutupnya otomatis."""
    with Session(engine) as session:
        yield session