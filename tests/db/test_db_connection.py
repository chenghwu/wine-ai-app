import pytest
from app.utils import env
from app.db.session import async_session
from sqlalchemy import text
import os

@pytest.mark.asyncio
async def test_db_session_basic():
    db_url = os.getenv("DATABASE_URL")
    assert db_url, "DATABASE_URL not set — check .env or env loading"

    async with async_session() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar() == 1, "DB connection failed — SELECT 1 did not return 1"