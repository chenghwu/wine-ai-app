from app.utils import env
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/wine")
print(f"----------------------------{DATABASE_URL}--------------------")

#  Initializes async connection to PostgreSQL DB
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,     # check connection before use
    pool_recycle=1800,      # recycle stale connections
)

# Create a session factory which is required to interact with DB
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to be used in FastAPI routes
# Each request gets its own DB session
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session