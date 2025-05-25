from app.db.crud.wine_summary import get_wine_summary_by_name, save_wine_summary
from app.models.mcp_model import MCPOutput
from app.services.llm.gemini_engine import parse_wine_query_with_gemini
from app.services.llm.search_and_summarize import summarize_wine_info
from app.services.rules.sat_analyzer import analyze_wine_profile
from app.utils.mock import generate_mock_summary
from app.utils.normalize import to_title_case_wine_name
import json
import logging
import time

logger = logging.getLogger(__name__)

EXPECTED_SUMMARY_KEYS = {
    "wine", "region", "grape_varieties", "appearance", "nose", "palate", "aging",
    "average_price", "quality", "analysis", "reference_source"
}

async def handle_wine_analysis_query(request):
    # Grab user's free-text query
    query = request.input.get("query", "").strip()
    if not query:
        return {"status": "error", "error": "Query is empty."}

    logger.info(f"Query received: '{query}'")

    result = parse_wine_query_with_gemini(query)
    winery, wine, vintage = result["winery"], result["wine_name"], result["vintage"]
    logger.info(f"Parsed wine info - winery: {winery}, wine: {wine}, vintage: {vintage}")

    wine_name = ""
    if wine.casefold() in winery.casefold():
        wine_name = f"{winery} {vintage}"
    elif winery.casefold() in wine.casefold():
        wine_name = f"{wine} {vintage}"
    else:
        wine_name = f"{winery} {wine} {vintage}"

    return {
        "wine_name": wine_name.strip(),
        "parsed_winery": winery,
        "parsed_wine": wine,
        "parsed_vinage": vintage,
        "original_query": query
    }

async def handle_mock_response(request):
    output = generate_mock_summary()
    return {
        "status": "mocked",
        "input": request.input,
        "output": output,
        "context": request.context.model_dump()
    }

async def handle_db_response(session, wine_name, request):
    existing = await get_wine_summary_by_name(session, wine_name)
    if existing:
        return {
            "status": "analyzed",
            "input": request.input,
            "output": MCPOutput(**existing.to_dict()),
            "context": request.context.model_dump()
        }
    return None

async def handle_invalid_summary(summary, request, error_message: str = "An unknown error occurred"):
    return {
        "status": "error",
        "error": summary.get("error", error_message),
        "input": request.input,
        "context": request.context.model_dump()
    }

async def handle_fresh_summary(session, wine_name, query, request):
    try:
        summary = await summarize_wine_info(wine_name)
    except Exception as e:
        logger.error(f"Error during wine summary: {e}")
        return await handle_invalid_summary(
            {"error": "Failed to summarize wine information. Please try again later."},
            request
        )

    if "error" in summary:
        logger.error(f"Summarization returned error: {summary['error']}")
        return await handle_invalid_summary(summary, request)

    missing_keys = EXPECTED_SUMMARY_KEYS - summary.keys()
    if missing_keys:
        logger.error(f"Missing key attributes from Gemini summary: {missing_keys}")
        return await handle_invalid_summary(
            {"error": "Incomplete wine analysis generated. Please retry."},
            request
        )

    # Ensure 'region' is not None before saving, default to "Unknown" if it is.
    # An empty string "" is acceptable.
    if summary.get('region') is None:
        summary['region'] = "Unknown"

    # SAT Rule-based analysis
    sat_result = analyze_wine_profile(summary)
    summary["sat"] = sat_result

    # Save to DB
    logger.info(f"Saving to DB: '{wine_name}'")

    summary_cleaned = summary.copy()   # Before changing schema, don't save aroma column to DB since it's in sat 
    summary_cleaned.pop("aroma", None)

    try:
        await save_wine_summary(session, {
            **summary_cleaned,
            "query_text": query
        })
    except Exception as e:
        logger.error(f"Failed to save summary to DB: {e}")
        # Non-blocking, still return successful response

    return {
        "status": "analyzed",
        "input": request.input,
        "output": MCPOutput(**summary_cleaned),
        "context": request.context.model_dump() # Ensure dict for JSON serialization
    }
