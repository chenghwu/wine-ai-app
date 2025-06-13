from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import WineSummary

async def get_wine_summary_by_name(session: AsyncSession, wine_name: str) -> WineSummary | None:
    result = await session.execute(
        select(WineSummary).where(WineSummary.wine.ilike(wine_name))
    )
    return result.scalars().first()

async def save_wine_summary(session: AsyncSession, data: dict):
    db_entry = WineSummary(**data)
    session.add(db_entry)
    await session.commit()

async def get_all_wine_summaries(session: AsyncSession) -> list[WineSummary]:
    result = await session.execute(select(WineSummary))
    return result.unique().scalars().all()