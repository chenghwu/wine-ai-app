import pytest
from app.db.database import get_async_session

@pytest.mark.asyncio
async def test_db_session_basic():
    session_generator = get_async_session()       # Create generator
    session = await anext(session_generator)       # Pull out the session
    assert session is not None                     # Basic check
    await session_generator.aclose()               # Close properly