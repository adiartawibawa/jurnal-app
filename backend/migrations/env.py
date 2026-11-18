from logging.config import fileConfig

from alembic import context
from sqlmodel import SQLModel

from backend.app.core.config import settings
from backend.app.core.dbase import engine

# Import semua model agar terdaftar di SQLModel.metadata.
# Setiap kali membuat model baru, import juga di sini.
from backend.app.models.user import RevokedToken, User  # noqa: F401

# Objek konfigurasi Alembic (membaca alembic.ini)
config = context.config

# Mengaktifkan logging sesuai konfigurasi di alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata inilah yang dibandingkan Alembic dengan isi database
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Mode offline: hanya menghasilkan SQL tanpa terhubung ke database."""
    context.configure(
        url=str(settings.DATABASE_URL),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Mode online: terhubung ke database lewat engine yang sama dengan aplikasi."""
    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()