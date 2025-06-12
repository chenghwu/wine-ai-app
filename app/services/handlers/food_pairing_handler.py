from app.db.crud.wine_summary import get_wine_summary_by_name
from app.models.mcp_model import FoodPairingMCPOutput
from app.prompts.food_pairing_prompt import generate_food_pairing_prompt
from app.services.llm.gemini_engine import call_gemini_sync_with_retry
import logging

logger = logging.getLogger(__name__)

EXPECTED_PAIRING_KEYS = {"food", "reason"}

async def handle_food_pairing(session, wine_name: str) -> dict:
    wine = await get_wine_summary_by_name(session, wine_name)
    if not wine:
        return {
            "status": "error",
            "error": f"Wine '{wine_name}' not found in database."
        }

    profile = wine.to_dict()
    prompt = generate_food_pairing_prompt(profile)

    try:
        result = call_gemini_sync_with_retry(prompt)
    except Exception as e:
        logger.exception(f"Failed to generate food pairing suggestions for {wine_name}.")
        return {
            "status": "error",
            "error": f"Failed to generate pairing for {wine_name}. Please try again later."
        }

    if not isinstance(result, list) or not all(set(p.keys()) >= EXPECTED_PAIRING_KEYS for p in result):
        logger.error(f"Invalid pairing result format: {result}")
        return {
            "status": "error",
            "error": f"Invalid format in generated pairings for {wine_name}."
        }

    return {
        "status": "paired",
        "input": {"wine_name": wine_name},
        "output": FoodPairingMCPOutput(
            wine_name=wine_name,
            pairings=result
        )
    }