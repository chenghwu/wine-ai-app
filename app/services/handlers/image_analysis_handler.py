from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from typing import Dict, Any

from app.services.image.image_validator import validate_image_file, sanitize_filename, ImageValidationError
from app.services.image.image_processor import ImageProcessor
from app.services.vision.gemini_vision import GeminiVisionAnalyzer
from app.services.handlers.wine_summary_handler import handle_fresh_summary
from app.models.mcp_model import WineImageMCPRequest, ImageAnalysisResult
from app.exceptions import GeminiApiError

logger = logging.getLogger(__name__)

async def handle_image_analysis(
    file: UploadFile, 
    request: WineImageMCPRequest,
    session: AsyncSession
) -> Dict[str, Any]:
    """
    Handle wine label image analysis request.
    
    Args:
        file: Uploaded image file
        request: Request context
        session: Database session
        
    Returns:
        Dict containing analysis result or error
    """
    try:
        # Step 1: Validate uploaded file
        logger.info(f"Processing image upload: {file.filename}")
        
        file_content = await file.read()
        filename = sanitize_filename(file.filename or "uploaded_image.jpg")
        content_type = file.content_type or "image/jpeg"
        
        # Validate the image
        try:
            validation_result = validate_image_file(file_content, filename, content_type)
            logger.info(f"Image validation passed: {validation_result}")
        except ImageValidationError as e:
            return {
                "status": "error",
                "error": f"Invalid image: {str(e)}"
            }
        
        # Step 2: Process image for analysis
        processor = ImageProcessor()
        try:
            base64_image, image_metadata = processor.process_for_analysis(file_content)
            logger.info(f"Image processing completed: {image_metadata}")
        except ValueError as e:
            return {
                "status": "error", 
                "error": f"Image processing failed: {str(e)}"
            }
        
        # Step 3: Analyze with Gemini Vision (or use mock if enabled)
        use_mock = request.context.use_mock if hasattr(request.context, 'use_mock') else False
        
        if use_mock:
            logger.info("Using mock response for image analysis")
            vision_result = {
                "wine_name": "Opus One",
                "winery": "Opus One Winery", 
                "vintage": "2019",
                "region": "Napa Valley",
                "country": "USA",
                "alcohol_content": "15.0%",
                "grape_varieties": ["Cabernet Sauvignon", "Merlot", "Petit Verdot", "Cabernet Franc"],
                "confidence": 0.95,
                "analysis_method": "mock_response"
            }
        else:
            vision_analyzer = GeminiVisionAnalyzer()
            try:
                vision_result = vision_analyzer.analyze_wine_label(base64_image, image_metadata)
                logger.info(f"Vision analysis completed: confidence={vision_result.get('confidence', 0)}")
            except GeminiApiError as e:
                return {
                    "status": "error",
                    "error": f"Vision analysis failed: {str(e)}"
                }
        
        # Step 4: Extract wine information and create query
        wine_info = extract_wine_query_from_vision(vision_result)
        
        if not wine_info["wine_query"]:
            return {
                "status": "error", 
                "error": "Could not extract wine information from image. Please try a clearer photo or enter the wine name manually."
            }
        
        # Step 5: Continue with standard wine analysis pipeline
        logger.info(f"Extracted wine query: '{wine_info['wine_query']}'")
        
        # Create a mock request for the wine analysis pipeline
        from app.models.mcp_model import WineMCPRequest
        wine_request = WineMCPRequest(
            input={"query": wine_info["wine_query"]},
            context=request.context
        )
        
        # Use the existing wine analysis pipeline
        wine_analysis = await handle_fresh_summary(
            session, 
            wine_info["wine_query"], 
            wine_info['wine_query'], 
            wine_request
        )
        
        # Add image analysis metadata to the response
        if wine_analysis.get("status") == "success" and "output" in wine_analysis:
            wine_analysis["output"]["image_analysis"] = {
                "extracted_info": vision_result,
                "confidence": vision_result.get("confidence", 0),
                "analysis_method": "gemini_vision"
            }
        
        return wine_analysis
        
    except Exception as e:
        logger.exception("Image analysis handler failed")
        return {
            "status": "error",
            "error": f"Analysis failed: {str(e)}"
        }

def extract_wine_query_from_vision(vision_result: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract a searchable wine query from vision analysis result.
    
    Args:
        vision_result: Result from Gemini Vision analysis
        
    Returns:
        Dict with wine_query and components
    """
    wine_name = vision_result.get("wine_name", "").strip()
    winery = vision_result.get("winery", "").strip()
    vintage = vision_result.get("vintage", "").strip() if vision_result.get("vintage") else ""
    
    # Build query components
    query_parts = []
    
    # Add winery if different from wine name
    if winery and winery.lower() not in wine_name.lower():
        query_parts.append(winery)
    
    # Add wine name
    if wine_name and wine_name.lower() != "unknown wine":
        query_parts.append(wine_name)
    
    # Add vintage if available
    if vintage and vintage.isdigit() and len(vintage) == 4:
        query_parts.append(vintage)
    
    wine_query = " ".join(query_parts).strip()
    
    return {
        "wine_query": wine_query,
        "wine_name": wine_name,
        "winery": winery, 
        "vintage": vintage,
        "confidence": vision_result.get("confidence", 0)
    }