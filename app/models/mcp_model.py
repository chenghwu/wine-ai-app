from pydantic import BaseModel, Field                # Base class for creating data models in FastAPI
from typing import Optional, Dict, List, Union, Any  # Typing support for flexible input/output fields
from datetime import datetime                        # For recording timestamp metadata

# Define the context metadata for the analysis
class MCPContext(BaseModel):
    model: str                                       # Name or ID of the model that generated the output (e.g., "sat-v1", "yolo-label-v2")
    timestamp: datetime                              # When was this analysis performed
    confidence: Optional[float] = None               # Score between 0 and 1 indicating model's confidence (e.g., 0.85)
    user_id: Optional[str] = None                    # Optionally record who made the request (for personalization or logging)
    ruleset: Optional[str] = None                    # Name of the logic applied (e.g., "WSET Level 3 SAT Rules")
    use_mock: Optional[bool] = False

class SATResult(BaseModel):
    score: int
    quality: str
    criteria: List[str]
    aroma: Dict[str, List[str]]
    clusters: Optional[List[str]] = None
    descriptors: Optional[List[str]] = None

class MCPOutput(BaseModel):
    wine: str
    grape_varieties: str
    appearance: str
    nose: str
    palate: str
    aging: str
    #quality: str
    average_price: str
    analysis: str
    sat: SATResult
    reference_source: List[str]

# Define the main request schema used in your FastAPI endpoint /analyze
class MCPRequest(BaseModel):
    input: Dict[str, Any] = Field(..., json_schema_extra={"example": {"query": "Opus One 2015"}})
    output: Optional[MCPOutput] = None
    context: MCPContext