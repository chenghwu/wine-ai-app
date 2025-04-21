from app.db.crud.wine_summary import get_wine_summary_by_name, save_wine_summary
from app.services.llm.search_and_summarize import summarize_wine_info
from app.services.rules.sat_analyzer import analyze_wine_profile
from app.models.mcp_model import MCPOutput
from app.utils.mock import generate_mock_summary
import logging

EXPECTED_SUMMARY_KEYS = {
    "wine", "appearance", "nose", "palate", "aging",
    "average_price", "quality", "analysis", "reference_source"
}

async def handle_mock_response(wine_name, request):
    output = generate_mock_summary(wine_name)
    return {
        "status": "mocked",
        "input": request.input,
        "output": output,
        "context": request.context.dict()
        }

async def handle_db_response(session, wine_name, request):
    existing = await get_wine_summary_by_name(session, wine_name)
    if existing:
        return {
            "status": "analyzed",
            "input": request.input,
            "output": MCPOutput(**existing.to_dict()),
            "context": request.context.dict()
        }
    return None

async def handle_invalid_summary(summary, request):
    return {
        "status": "error",
        "input": request.input,
        "output": summary,
        "context": request.context.dict()
    }

async def handle_fresh_summary(session, wine_name, query, request):
    summary = await summarize_wine_info(wine_name)

    missing_keys = EXPECTED_SUMMARY_KEYS - summary.keys()
    if missing_keys:
        logger.error(f"Missing key attributes from Gemini summary: {missing_keys}")
        return await handle_invalid_summary(summary, request)

    if "error" in summary:
        return await handle_invalid_summary(summary, request)

    # SAT Rule-based analysis
    summary["sat"] = analyze_wine_profile(summary)

    logger = logging.getLogger(__name__)
    logger.info(f"Save to DB: '{wine_name}'")
    
    # Save to DB
    try:
        await save_wine_summary(session, {
            **summary,
            "query_text": query
        })
    except Exception as e:
        logger.error(f"Failed to save summary to DB: {e}")

    return {
        "status": "analyzed",
        "input": request.input,
        "output": MCPOutput(**summary),
        "context": request.context.dict()  # Ensure dict for JSON serialization
    }
