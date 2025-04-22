import os
from logging.config import fileConfig
from pathlib import Path

# Use sync engine since Alembic doesn't officially support async engines directly
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import URL
from alembic import context
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load .env file to populate os.environ
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")

# Alembic Config
config = context.config

# Optional: Configure Alembic logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models' metadata
from app.db.models import Base
target_metadata = Base.metadata

def build_db_url():
    return URL.create(
            "postgresql+psycopg2",
            username=os.getenv("DB_USER", "wine_user"),
            password=quote_plus(os.getenv("DB_PASSWORD", "wine_pass")),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "winesearchdb")
    )

# Offline migration logic
def run_migrations_offline():
    """Run migrations without connecting to DB (offline)."""
    url = build_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True   # ensure Alembic detects type changes
    )

    with context.begin_transaction():
        context.run_migrations()

# Online migration logic
def run_migrations_online():
    """Run migrations connected to DB."""
    url = build_db_url()
    connectable = create_engine(url, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

# Entry point
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()