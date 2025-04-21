from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/wine")

#  Initializes async connection to PostgreSQL DB
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session factory which is required to interact with DB
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Dependency to be used in FastAPI routes
# Each request gets its own DB session
async def get_async_session() -> AsyncSession:
    async with async_session() as session:
        yield session