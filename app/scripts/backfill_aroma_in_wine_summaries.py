import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from app.db.session import async_session
from app.db.models.wine_summary import WineSummary
from app.constants.aroma_lexicons import AROMA_LEXICONS

def rebuild_aroma_from_descriptors(descriptors: list[str]) -> dict[str, list[str]]:
    aroma = {}
    for cluster, keywords in AROMA_LEXICONS.items():
        matches = [d for d in descriptors if d in keywords]
        if matches:
            aroma[cluster] = sorted(set(matches))
    return aroma

async def backfill_aroma():
    async with async_session() as session:  # type: AsyncSession
        stmt = select(WineSummary)
        results = await session.execute(stmt)
        summaries = results.scalars().all()

        updated = 0

        for summary in summaries:
            sat = summary.sat

            if not sat or "aroma" in sat:
                continue  # skip if no sat or already has aroma

            descriptors = sat.get("descriptors", [])
            if not descriptors:
                continue

            aroma = rebuild_aroma_from_descriptors(descriptors)

            # Update the sat dict
            sat["aroma"] = aroma

            # Assign it back so SQLAlchemy sees the change
            summary.sat = sat

            # Force SQLAlchemy to recognize the update
            flag_modified(summary, "sat")

            updated += 1
            print(f"Updated {summary.wine}")

        await session.commit()
        print(f"Backfilled aroma in {updated} records.")

if __name__ == "__main__":
    asyncio.run(backfill_aroma())