import os, logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.wine_summary import get_all_wine_summaries
from app.db.session import get_async_session
from app.exceptions import GoogleSearchApiError, GeminiApiError
from app.models.mcp_model import MCPRequest
from app.services.handlers.wine_summary_handler import (
    handle_wine_analysis_query, handle_mock_response, handle_db_response, handle_fresh_summary
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Extract user query, use Google Programmable Search Engine and Gemini to search and aggregate info
@router.post("/chat-search-wine", summary="Search wine info using LLM and return SAT-style analysis")
async def chat_search_wine(request: MCPRequest, session: AsyncSession = Depends(get_async_session)):
    env = os.getenv("ENV", "prod")
    use_mock = request.context.model_dump().get("use_mock", False)
    
    # Mock logic (only in local dev mode)
    if env == "dev" and use_mock:
        logger.info("Using mock response in local dev mode.")
        return await handle_mock_response(request)

    # Parse user query into structured wine info
    try:
        parsed = await handle_wine_analysis_query(request)
        wine_name = parsed["wine_name"]
        original_query = parsed["original_query"]

        # Check if summary already exists in DB
        cached = await handle_db_response(session, wine_name, request)
        if cached:
            logger.info(f"Found existing summary in DB.")
            return cached

        # Summarize the wine info using smart search + LLM pipeline
        return await handle_fresh_summary(session, wine_name, original_query, request)

    except GoogleSearchApiError as e:
        logger.exception("Google Search API failed.")
        return {
            "status": "error",
            "error": "Having trouble fetching information. Please try again later."
        }
    except GeminiApiError as e:
        logger.exception("Gemini summarization failed.")
        return {
            "status": "error",
            "error": "Couldn't generate tasting analysis. Please retry shortly."
        }
    except Exception as e:
        logger.exception("Failed to process wine analysis request.")
        return {
            "status": "error",
            "error": "Something went wrong while analyzing the wine. Please try again later."
        }

@router.get("/wines", summary="Get all stored wine summaries")
async def list_all_wines(session: AsyncSession = Depends(get_async_session)):
    results = await get_all_wine_summaries(session)
    return [wine.to_dict() for wine in results]

@router.api_route("/healthcheck", methods=["GET", "HEAD"], summary="Healthcheck endpoints")
async def healthcheck(
    deep: bool = Query(default=False),
    session: AsyncSession = Depends(get_async_session)
):
    if not deep:
        # Shallow healthcheck (only server status)
        return {"status": "healthy"}

    try:
        # Deep healthcheck (include DB check)
        await session.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.exception("Deep DB healthcheck failed.")
        return {"status": "unhealthy", "database": "unreachable", "error": str(e)}

@router.get("/meta", summary="App metadata")
async def get_metadata():
    from app.version import APP_VERSION, LAST_UPDATED

    return {
        "version": APP_VERSION,
        "last_updated": LAST_UPDATED,
    }