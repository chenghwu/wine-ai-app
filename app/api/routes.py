from fastapi import APIRouter
from app.models.mcp_model import MCPRequest, MCPOutput
from app.analyzers.sat_analyzer import analyze_wine_profile  # Import the SAT scoring engine
from app.services.llm.llm_agent import summarize_with_gemini
from app.services.llm.search_and_summarize import summarize_wine_info
from app.utils.search import google_search_links

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
async def chat_search_wine(request: MCPRequest):
    # Grab user's free-text query
    query = request.input.get("query", "").strip()

    ''' TODO:
    # Use Gemini to extract wine info
    parsed = parse_wine_query_with_llm(query)
    '''

    # Step 1: Summarize the wine info using your smart search pipeline
    sat_result = summarize_wine_info(query)

    # Step 2: Rule-based analysis if needed
    sat_result["analysis"] = analyze_wine_profile(sat_result)

    # Step 3: Ensure structure is complete
    sat_result.setdefault("reference_source", [])
    sat_result.setdefault("average_price", "N/A")

    # Step 4: Wrap response using MCPOutput
    output = MCPOutput(**sat_result)

    return {
        "status": "analyzed",
        "input": request.input,
        "output": output,
        "context": request.context.dict()  # Ensure dict for JSON serialization
    }