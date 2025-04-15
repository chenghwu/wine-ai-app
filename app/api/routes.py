from fastapi import APIRouter
from app.models.mcp_model import MCPRequest
from app.services.analyzer import analyze_sat_profile   # Import the SAT scoring engine

router = APIRouter()

@router.post("/analyze", summary="Analyze wine and return SAT profile")
async def analyze_wine(request: MCPRequest):    # MCPRequest is a Pydantic model ensures wrapping the request in MCP format
    # Extract input section from MCP
    wine_input = request.input

    # Run the WSET SAT scoring engine
    sat_result = analyze_sat_profile(wine_input)

    # Construct new MCP-compatible response
    return {
        "status": "analyzed",
        "input": wine_input,
        "output": sat_result,
        "context": request.context.dict()  # Keep original context metadata
    }