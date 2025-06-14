from app.db.models.food_pairing import FoodPairingCategory, FoodPairingExample
from app.db.models.wine_summary import WineSummary
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional

async def save_food_pairings(session, wine_id: int, data: list[dict]):
    # data = [{"category": "Beef", "examples": [{"food": "...", "reason": "..."}, ...]}, ...]
    for group in data:
        cat = FoodPairingCategory(
            wine_id=wine_id,
            category=group["category"],
            base_category=group["base_category"]
        )
        session.add(cat)
        await session.flush()  # Get cat.id

        for item in group["examples"]:
            example = FoodPairingExample(
                category_id=cat.id,
                food=item["food"],
                reason=item["reason"]
            )
            session.add(example)

    await session.commit()

# Retrieve wine summary and its pairings for a given wine
async def get_wine_and_pairings(session: AsyncSession, wine_name: str) -> tuple[Optional[WineSummary], list[FoodPairingCategory]]:
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    result = await session.execute(
        select(WineSummary)
        .options(selectinload(WineSummary.food_pairing_categories).selectinload(FoodPairingCategory.examples))
        .where(WineSummary.wine.ilike(wine_name))
    )
    wine = result.scalar_one_or_none()
    categories = wine.food_pairing_categories if wine else []
    return wine, categories