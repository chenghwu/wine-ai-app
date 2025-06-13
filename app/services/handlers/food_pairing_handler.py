from app.db.crud.wine_summary import get_wine_summary_by_name
from app.db.crud.food_pairing import save_food_pairings
from app.db.models import WineSummary
from app.models.mcp_model import FoodPairingMCPOutput, FoodPairingCategory
from app.prompts.food_pairing_prompt import generate_food_pairing_prompt
from app.services.llm.gemini_engine import call_gemini_sync_with_retry
from app.utils.llm_parsing import parse_json_from_text
from pydantic import ValidationError
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def handle_cached_pairings(session, wine_name: str) -> tuple[dict | None, object | None]:
    from app.db.models import FoodPairingCategory as DBFoodPairingCategory, WineSummary
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    result = await session.execute(
        select(WineSummary)
        .options(selectinload(WineSummary.food_pairing_categories).selectinload(DBFoodPairingCategory.examples))
        .where(WineSummary.wine.ilike(wine_name))
    )
    wine = result.scalar_one_or_none()

    if wine and wine.food_pairing_categories:
        return {
            "status": "cached",
            "input": {"wine_name": wine_name},
            "output": FoodPairingMCPOutput(
                wine=wine_name,
                pairings=[cat.to_dict() for cat in wine.food_pairing_categories]
            )
        }, wine

    return None, wine  # Return wine even if no pairings exist

async def handle_food_pairing(session, wine_name: str, wine: Optional[WineSummary] = None) -> dict:
    if not wine:
        wine = await get_wine_summary_by_name(session, wine_name)
        if not wine:
            return {
                "status": "error",
                "error": f"Wine '{wine_name}' not found in database."
            }

    profile = wine.to_dict()
    prompt = generate_food_pairing_prompt(profile)

    try:
        raw_text = call_gemini_sync_with_retry(prompt)
        logger.info(f"Gemini raw output:\n{raw_text}")
        parsed = parse_json_from_text(raw_text)
        if not isinstance(parsed, list):
            raise ValueError("Parsed result is not a list of pairing categories.")

    except Exception as e:
        logger.exception(f"Failed to generate food pairing suggestions for {wine_name}.")
        return {
            "status": "error",
            "error": f"Failed to generate pairing for {wine_name}. Please try again later."
        }
    
    # Validate result format from Gemini
    try:
        validated_pairings = [FoodPairingCategory.parse_obj(p) for p in parsed]
    except ValidationError as ve:
        logger.error(f"Validation error for {wine_name}: {ve}")
        return {
            "status": "error",
            "error": f"Invalid format in generated pairings for {wine_name}."
        }
    
    pairing_dicts = [p.dict() for p in validated_pairings]

    # Save to DB
    try:
        await save_food_pairings(session, wine.id, pairing_dicts)
        logger.info(f"Saved food pairings for wine '{wine_name}'")
    except Exception as e:
        logger.error(f"Failed to save pairings to DB for {wine_name}: {e}")
        # Non-blocking, still return the successful response

    return {
        "status": "paired",
        "input": {"wine_name": wine_name},
        "output": FoodPairingMCPOutput(
            wine=wine_name,
            pairings=pairing_dicts
        )
    }