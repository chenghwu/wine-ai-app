import os
from fastapi import APIRouter, Depends
from app.models.mcp_model import MCPRequest, MCPOutput
from app.analyzers.sat_analyzer import analyze_wine_profile  # Import the SAT scoring engine
from app.services.llm.llm_agent import summarize_with_gemini
from app.services.llm.search_and_summarize import summarize_wine_info
from app.utils.search import google_search_links
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_async_session
from sqlalchemy import text
from app.db.crud.wine_summary import get_wine_summary_by_name, save_wine_summary, get_all_wine_summaries
from app.db.models.wine_summary import WineSummary
from app.db.session import get_async_session

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
    # Step 1: Grab user's free-text query
    query = request.input.get("query", "").strip()

    # Step 2: Check if mock should be used (only in dev mode)
    use_mock = request.context.dict().get("use_mock", False)

    ''' TODO:
    # Use Gemini to extract wine info
    parsed = parse_wine_query_with_llm(query)
    '''

    wine_name = query

    print(f"Searching for: {wine_name}")

    env = os.getenv("ENV", "prod")
    if env == "dev" and use_mock == True:
        print("Dev mode returning mock response:")
        return {
            "wine": wine_name,
            "appearance": "Deep ruby",
            "nose": "Medium+ aromas of cassis, tobacco, mocha",
            "palate": "Full-bodied, high acidity, ripe tannins, long finish",
            "aging": "Can age 8–12 years",
            "average_price": "$120",
            "analysis": f"""Based on the information available, it has complex aroma and flavor profile,
                            with red and black fruit, spice, and earthy notes.
                            The structure (tannins, acidity, alcohol) suggests good aging potential.""",
            "sat": {
                "score": 3,
                "quality": "Very Good",
                "criteria": ["Balance", "Length", "Complexity"],
                "clusters": ["Black fruit"],
                "descriptors": ["cassis", "tobacco", "mocha"]
            },
            "reference_source": ["wineSpectator.com"]
        }

    # Step 3: Check if summary already exists in DB
    existing = await get_wine_summary_by_name(session, wine_name)
    if existing:
        print("Found existing summary in DB.")
        return existing.to_dict()   # Make sure WineSummary has .to_dict()

    # Step 4: Summarize the wine info using smart search + LLM pipeline
    # Need to make sure Gemini output satisfy MCPOutput model
    wine_summary = await summarize_wine_info(query)

    expected_keys = {
        "wine", "appearance", "nose", "palate", "aging",
        "average_price", "quality", "analysis", "reference_source"
    }

    if not expected_keys.issubset(wine_summary.keys()):
        print("Gemini returned format error!!!", wine_summary.keys())
        return {
            "error": "Gemini returned invalid format."
        }

    if "error" in wine_summary:
        return {
            "status": "error",
            "input": request.input,
            "output": wine_summary,
            "context": request.context.dict()
        }

    # Step 5: SAT Rule-based analysis
    sat_result = analyze_wine_profile(wine_summary)

    # Inject required fields
    wine_summary["sat"] = sat_result
    wine_summary["query_text"] = query

    # Step 6: Save to DB
    await save_wine_summary(session, wine_summary)

    # For MCPOutput schema — required top-level field
    #wine_summary["quality"] = sat_result.get("structured_quality", "N/A")

    # Step 7: Wrap response using MCPOutput
    output = MCPOutput(**wine_summary)

    return {
        "status": "analyzed",
        "input": request.input,
        "output": output,
        "context": request.context.dict()  # Ensure dict for JSON serialization
    }

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