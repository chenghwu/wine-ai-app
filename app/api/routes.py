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
    # Step 1: Grab user's free-text query
    query = request.input.get("query", "").strip()

    # Step 2: Check if mock should be used (only in dev mode)
    use_mock = request.context.dict().get("use_mock", False)

    ''' TODO:
    # Use Gemini to extract wine info
    parsed = parse_wine_query_with_llm(query)
    '''

    # Step 3: Summarize the wine info using smart search + LLM pipeline
    # Need to make sure Gemini output satisfy MCPOutput model
    wine_summary = summarize_wine_info(query, use_mock)

    expected_keys = {
        "wine", "appearance", "nose", "palate", "aging",
        "average_price", "quality", "analysis", "reference_source"
    }

    if not expected_keys.issubset(wine_summary.keys()):
        print("Gemini returned format error!!!", wine_summary.keys())
        return {
            "error": "Gemini returned invalid format."
        }
    print("Returning response:", wine_summary.get("reference_source"))

    if "error" in wine_summary:
        return {
            "status": "error",
            "input": request.input,
            "output": wine_summary,
            "context": request.context.dict()
        }

    # Step 4: SAT Rule-based analysis
    sat_result = analyze_wine_profile(wine_summary)
    wine_summary["sat"] = sat_result

    # For MCPOutput schema — required top-level field
    #wine_summary["quality"] = sat_result.get("structured_quality", "N/A")

    # Step 5: Ensure structure is complete for MCPOutput
    #wine_summary.setdefault("average_price", "N/A")
    #wine_summary.setdefault("reference_source", [])

    # Step 6: Wrap response using MCPOutput
    output = MCPOutput(**wine_summary)

    return {
        "status": "analyzed",
        "input": request.input,
        "output": output,
        "context": request.context.dict()  # Ensure dict for JSON serialization
    }