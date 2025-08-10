import logging
from typing import Dict, Any
from fastapi import UploadFile
from app.services.image.image_validator import validate_image_file
from app.services.image.image_processor import ImageProcessor
from app.services.vision.gemini_vision import GeminiVisionAnalyzer
from app.services.pairing.wine_recommender import WineRecommender
from app.utils.cache import cache_menu_analysis, get_cached_menu_analysis, generate_image_hash
from app.exceptions import GeminiApiError, ImageValidationError
from app.models.mcp_model import MenuMCPRequest

logger = logging.getLogger(__name__)

async def handle_menu_analysis(file: UploadFile, request: MenuMCPRequest) -> Dict[str, Any]:
    """
    Main handler for menu image analysis workflow.
    
    Steps:
    1. Validate and process uploaded image
    2. Check cache for existing analysis
    3. Extract menu items using Gemini Vision
    4. Generate wine recommendations
    5. Return structured results
    
    Args:
        file: Uploaded menu image file
        request: Menu analysis request with MCP context
        
    Returns:
        Dict containing menu items and wine recommendations
    """
    try:
        logger.info(f"Starting menu analysis for file: {file.filename}")
        
        # Step 1: Validate and process image
        file_content = await file.read()
        
        # Validate the image
        try:
            validation_result = validate_image_file(
                file_content=file_content,
                filename=file.filename or "menu.jpg",
                content_type=file.content_type or "image/jpeg"
            )
            logger.info(f"Image validation passed: {validation_result}")
        except ImageValidationError as e:
            return {
                "status": "error",
                "error": f"Image validation failed: {str(e)}"
            }
        
        # Generate image hash for caching
        image_hash = generate_image_hash(file_content)
        logger.info(f"Generated image hash: {image_hash}")
        
        # Step 2: Check cache for existing menu analysis
        cached_result = get_cached_menu_analysis(image_hash)
        if cached_result:
            logger.info("Using cached menu analysis result")
            return cached_result
        
        # Step 3: Process image for analysis
        image_processor = ImageProcessor()
        try:
            base64_image, image_metadata = image_processor.process_for_analysis(file_content)
            logger.info(f"Image processed: {image_metadata}")
        except Exception as e:
            return {
                "status": "error",
                "error": f"Image processing failed: {str(e)}"
            }
        
        # Step 4: Analyze with Gemini Vision (or use mock if enabled)
        use_mock = getattr(request.context, 'use_mock', False)
        
        if use_mock:
            logger.info("Using mock response for menu analysis")
            vision_result = {
                "restaurant_name": "The French Laundry",
                "cuisine_style": "French",
                "menu_items": [
                    {
                        "dish_name": "Pan-Seared Duck Breast with Cherry Gastrique",
                        "category": "main",
                        "price": "$38",
                        "ingredients": ["duck breast", "cherry", "gastrique sauce"],
                        "protein": "duck",
                        "cooking_method": "pan-seared",
                        "cuisine_type": "French",
                        "flavor_profile": ["rich", "sweet", "savory"],
                        "description": "Perfectly cooked duck breast with house-made cherry gastrique"
                    },
                    {
                        "dish_name": "Pan-Seared Halibut with Lemon Butter",
                        "category": "main",
                        "price": "$32",
                        "ingredients": ["halibut", "lemon", "butter", "herbs"],
                        "protein": "fish",
                        "cooking_method": "pan-seared",
                        "cuisine_type": "French",
                        "flavor_profile": ["light", "citrusy", "buttery"],
                        "description": "Fresh halibut with classic lemon butter sauce"
                    }
                ],
                "confidence": 0.95,
                "analysis_method": "mock_response"
            }
        else:
            vision_analyzer = GeminiVisionAnalyzer()
            try:
                vision_result = vision_analyzer.analyze_menu(base64_image, image_metadata)
                logger.info(f"Menu vision analysis completed: confidence={vision_result.get('confidence', 0)}")
            except GeminiApiError as e:
                return {
                    "status": "error",
                    "error": f"Menu vision analysis failed: {str(e)}"
                }
        
        # Step 5: Generate wine recommendations
        wine_recommender = WineRecommender()
        menu_items = vision_result.get('menu_items', [])
        
        if not menu_items:
            return {
                "status": "error",
                "error": "No menu items found in the image"
            }
        
        try:
            wine_recommendations = wine_recommender.recommend_wines_for_menu(
                menu_items=menu_items,
                use_mock=use_mock
            )
            logger.info(f"Wine recommendations generated for {len(menu_items)} items")
        except Exception as e:
            logger.error(f"Wine recommendation generation failed: {e}")
            # Use fallback recommendations
            wine_recommendations = {
                "menu_items": [
                    {
                        "dish": item,
                        "wine_pairings": wine_recommender._get_fallback_recommendations(item)
                    }
                    for item in menu_items
                ],
                "overall_recommendations": [{
                    "category": "Balanced Selection",
                    "recommendation": "Mix of medium-bodied reds and crisp whites",
                    "reasoning": "Safe pairing approach for diverse menu"
                }],
                "analysis_method": "fallback"
            }
        
        # Step 6: Combine results
        final_result = {
            "status": "success",
            "restaurant_info": {
                "name": vision_result.get('restaurant_name'),
                "cuisine_style": vision_result.get('cuisine_style', 'Unknown'),
                "confidence": vision_result.get('confidence', 0.8)
            },
            "menu_analysis": {
                "items_found": len(menu_items),
                "extraction_method": vision_result.get('analysis_method', 'gemini_vision'),
                "raw_menu_items": menu_items
            },
            "wine_recommendations": wine_recommendations,
            "image_metadata": {
                "hash": image_hash,
                "processing_info": image_metadata,
                "original_filename": file.filename
            },
            "analysis_metadata": {
                "use_mock": use_mock,
                "timestamp": image_metadata.get('processed_at'),
                "cache_key": image_hash
            }
        }
        
        # Step 7: Cache the results
        cache_menu_analysis(image_hash, final_result, ttl_minutes=15)
        
        logger.info("Menu analysis completed successfully")
        return final_result
        
    except Exception as e:
        logger.error(f"Menu analysis handler failed: {e}")
        return {
            "status": "error",
            "error": f"Menu analysis failed: {str(e)}",
            "details": "Please try again or contact support if the issue persists"
        }


def extract_food_query_from_menu(menu_result: Dict[str, Any]) -> str:
    """
    Extract a searchable food query from menu analysis result.
    Used as fallback to convert menu items into wine search queries.
    
    Args:
        menu_result: Result from menu vision analysis
        
    Returns:
        String query describing the menu items for wine pairing
    """
    menu_items = menu_result.get('menu_items', [])
    
    if not menu_items:
        return "mixed cuisine menu"
    
    # Extract key characteristics
    proteins = []
    cooking_methods = []
    cuisines = []
    
    for item in menu_items:
        if item.get('protein'):
            proteins.append(item['protein'])
        if item.get('cooking_method'):
            cooking_methods.append(item['cooking_method'])
        if item.get('cuisine_type'):
            cuisines.append(item['cuisine_type'])
    
    # Create descriptive query
    query_parts = []
    
    if proteins:
        unique_proteins = list(set(proteins))
        query_parts.append(f"menu with {', '.join(unique_proteins[:3])}")
    
    if cuisines:
        unique_cuisines = list(set(cuisines))
        query_parts.append(f"{unique_cuisines[0]} cuisine")
    
    if cooking_methods:
        unique_methods = list(set(cooking_methods))
        query_parts.append(f"{unique_methods[0]} preparations")
    
    return " ".join(query_parts) or "restaurant menu items"


async def handle_food_text_analysis(food_description: str, request: MenuMCPRequest) -> Dict[str, Any]:
    """
    Handle text-based food description for wine recommendations.
    Alternative to image-based menu analysis.
    
    Args:
        food_description: User's text description of food/dish
        request: Menu analysis request with MCP context
        
    Returns:
        Dict containing wine recommendations for the described food
    """
    try:
        logger.info(f"Starting food text analysis: {food_description}")
        
        # Create a mock menu item from text description
        mock_menu_item = {
            "dish_name": food_description,
            "category": "main",
            "price": None,
            "ingredients": food_description.split(),  # Simple word splitting
            "protein": "unknown",  # Could be enhanced with NLP
            "cooking_method": "unknown",
            "cuisine_type": "unknown",
            "flavor_profile": [],
            "description": food_description
        }
        
        # Generate wine recommendations
        wine_recommender = WineRecommender()
        use_mock = getattr(request.context, 'use_mock', False)
        
        wine_recommendations = wine_recommender.recommend_wines_for_menu(
            menu_items=[mock_menu_item],
            use_mock=use_mock
        )
        
        return {
            "status": "success",
            "input_type": "text_description",
            "food_description": food_description,
            "wine_recommendations": wine_recommendations,
            "analysis_metadata": {
                "use_mock": use_mock,
                "input_method": "text"
            }
        }
        
    except Exception as e:
        logger.error(f"Food text analysis failed: {e}")
        return {
            "status": "error",
            "error": f"Text analysis failed: {str(e)}"
        }