from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.models.food_pairing import FoodPairingCategory, FoodPairingExample
from app.db.models.wine_summary import WineSummary

# Save pairings to DB
def group_pairings_by_category(pairings):
    grouped = {}
    for item in pairings:
        category = item.get("category", "General")
        grouped.setdefault(category, []).append({
            "food": item["food"],
            "reason": item["reason"]
        })
    return grouped

async def save_food_pairings(session, wine_id: int, data: list[dict]):
    # data = [{"category": "Beef", "examples": [{"food": "...", "reason": "..."}, ...]}, ...]
    for group in data:
        cat = FoodPairingCategory(wine_id=wine_id, category=group["category"])
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

# Retrieve pairings for a given wine
async def get_pairings_by_name(session: AsyncSession, wine_name: str):
    result = await session.execute(
        select(FoodPairingCategory)
        .join(WineSummary)
        .options(selectinload(FoodPairingCategory.examples))
        .where(WineSummary.wine == wine_name)
    )
    categories = result.scalars().all()

    return [
        {
            "category": cat.category,
            "examples": [{"food": e.food, "reason": e.reason} for e in cat.examples]
        }
        for cat in categories
    ]