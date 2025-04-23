from app.db.crud.wine_summary import get_wine_summary_by_name, save_wine_summary
from app.models.mcp_model import MCPOutput
from app.services.llm.gemini_engine import parse_wine_query_with_gemini
from app.services.llm.search_and_summarize import summarize_wine_info
from app.services.rules.sat_analyzer import analyze_wine_profile
from app.utils.mock import generate_mock_summary
from app.utils.normalize import to_title_case_wine_name
import logging

logger = logging.getLogger(__name__)

EXPECTED_SUMMARY_KEYS = {
    "wine", "appearance", "nose", "palate", "aging",
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
    logger.info(f"Parsed wine info - 'winery: {winery}, wine: {wine}, vintage: {vintage}")

    wine_name = ""
    if winery.casefold() == wine.casefold():
        wine_name = f"{winery} {vinage}"
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
    
    # Save to DB
    logger.info(f"Saving to DB: '{wine_name}'")
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
