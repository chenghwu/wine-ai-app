from pydantic import BaseModel                       # Base class for creating data models in FastAPI
from typing import Optional, Dict, Any               # Typing support for flexible input/output fields
from datetime import datetime                        # For recording timestamp metadata

# Define the context metadata for the analysis
class MCPContext(BaseModel):
    model: str                                       # Name or ID of the model that generated the output (e.g., "sat-v1", "yolo-label-v2")
    timestamp: datetime                              # When was this analysis performed
    confidence: Optional[float] = None               # Score between 0 and 1 indicating model's confidence (e.g., 0.85)
    user_id: Optional[str] = None                    # Optionally record who made the request (for personalization or logging)
    ruleset: Optional[str] = None                    # Name of the logic applied (e.g., "WSET Level 3 SAT Rules")

# Define the main request schema used in your FastAPI endpoint /analyze
class MCPRequest(BaseModel):
    input: Dict[str, Any]
    output: Dict[str, Any]
    context: MCPContext