from app.db.crud.wine_summary import get_wine_summary_by_name
from app.prompts.food_pairing_prompt import generate_food_pairing_prompt
from app.services.llm.gemini_engine import call_gemini_sync_with_retry
import logging

logger = logging.getLogger(__name__)

async def handle_food_pairing(session, wine_name: str) -> dict:
    wine = await get_wine_summary_by_name(session, wine_name)
    if not wine:
        return {"error": f"Wine '{wine_name}' not found in database."}

    profile = wine.to_dict()
    prompt = generate_food_pairing_prompt(profile)

    try:
        response = call_gemini_sync_with_retry(prompt)
        return {
            "wine_name": wine_name,
            "pairings": response
        }
    except Exception as e:
        logger.exception("Failed to generate food pairing.")
        return {"error": "Failed to generate pairing. Please try again later."}