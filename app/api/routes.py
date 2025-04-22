import os, logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.wine_summary import get_all_wine_summaries
from app.db.session import get_async_session
from app.models.mcp_model import MCPRequest
from app.services.handlers.wine_summary_handler import (
    handle_mock_response, handle_db_response, handle_fresh_summary, handle_invalid_summary
)

router = APIRouter()

# Directly pass structured query to LLM for SAT-style output
@router.post("/search-wine", summary="Search wine info using LLM and return SAT-style analysis")
async def search_wine(request: MCPRequest):  
    return {
        "status": "searched",
        "input": request.input,
        "output": generate_wine_analysis_from_llm(request.input),
        "context": request.context.dict()
    }

# Extract user query, use Gimini to search and aggregate info
@router.post("/chat-search-wine", summary="Search wine info using LLM and return SAT-style analysis")
async def chat_search_wine(request: MCPRequest, session: AsyncSession = Depends(get_async_session)):
    # Grab user's free-text query
    query = request.input.get("query", "").strip()
    if not query:
        return {"status": "error", "error": "Query is empty."}

    ''' TODO:
    # Use Gemini to extract wine info like wine name
    parsed_info = parse_wine_query_with_llm(query)
    '''

    env = os.getenv("ENV", "prod")
    use_mock = request.context.dict().get("use_mock", False)
    wine_name = query

    logger = logging.getLogger(__name__)
    logger.info(f"Query received: '{wine_name}'")

    # Check if mock should be used (only in dev mode)
    if env == "dev" and use_mock:
        return await handle_mock_response(wine_name, request)

    # Check if summary already exists in DB
    cached = await handle_db_response(session, wine_name, request)
    if cached:
        logger.info(f"Found existing summary in DB.")
        return cached

    # Summarize the wine info using smart search + LLM pipeline
    return await handle_fresh_summary(session, wine_name, query, request)

@router.get("/wines", summary="Get all stored wine summaries")
async def list_all_wines(session: AsyncSession = Depends(get_async_session)):
    results = await get_all_wine_summaries(session)
    return [wine.to_dict() for wine in results]

# To chek DB connectivity
@router.get("/db-test", summary="Check DB connectivity")
async def db_test(session: AsyncSession = Depends(get_async_session)):
    try:
        result = await session.execute(text("SELECT 1"))
        return {"db_working": True}
    except Exception as e:
        print("DB connection error:", e)
        return {"db_working": False}