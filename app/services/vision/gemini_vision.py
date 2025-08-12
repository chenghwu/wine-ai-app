import google.generativeai as genai
import base64
import logging
from typing import Dict, Any, Optional
from app.exceptions import GeminiApiError
from app.utils.env import setup_gemini_env
from app.utils.llm_parsing import parse_json_from_text

logger = logging.getLogger(__name__)

class GeminiVisionAnalyzer:
    """
    Gemini Vision API integration for wine label analysis.
    """
    
    def __init__(self):
        self.api_key, self.model_name, self.model = setup_gemini_env()
        
    def analyze_wine_label(self, base64_image: str, image_metadata: dict) -> Dict[str, Any]:
        """
        Analyze wine label using Gemini Vision API.
        
        Args:
            base64_image: Base64 encoded image
            image_metadata: Image processing metadata
            
        Returns:
            Dict containing extracted wine information
        """
        try:
            # Create the prompt for wine label analysis
            prompt = self._create_wine_label_prompt()
            
            # Prepare image for Gemini
            image_data = {
                'mime_type': 'image/jpeg',
                'data': base64_image
            }
            
            # Call Gemini Vision API
            response = self.model.generate_content(
                [prompt, image_data],
                generation_config={"temperature": 0.3}  # Lower temperature for more factual extraction
            )
            
            # Parse the response
            raw_text = response.text
            logger.info(f"Gemini Vision raw output: {raw_text}")
            
            # Try to parse as JSON, fall back to text parsing
            try:
                parsed_result = parse_json_from_text(raw_text)
            except Exception as e:
                logger.warning(f"JSON parsing failed, using text parsing: {e}")
                parsed_result = self._parse_text_response(raw_text)
            
            # Add metadata
            parsed_result['image_metadata'] = image_metadata
            parsed_result['analysis_method'] = 'gemini_vision'
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"Gemini Vision analysis failed: {e}")
            raise GeminiApiError(f"Vision analysis failed: {str(e)}")
    
    def _create_wine_label_prompt(self) -> str:
        """
        Create detailed prompt for wine label analysis.
        """
        return """
You are a wine expert analyzing a wine label image. Extract all visible information from the wine label and return it in JSON format.

Focus on extracting these key elements:
1. **Wine Name**: The primary wine name/brand
2. **Winery/Producer**: The winery or producer name
3. **Vintage**: Year the wine was produced
4. **Region/Appellation**: Geographic origin (e.g., "Napa Valley", "Bordeaux", "Barolo")
5. **Grape Varieties**: Types of grapes used (e.g., "Cabernet Sauvignon", "Pinot Noir")
6. **Alcohol Content**: ABV percentage if visible
7. **Wine Type**: Red, White, Rosé, Sparkling, etc.
8. **Additional Info**: Any other relevant details (reserve, estate, organic, etc.)

If text is partially obscured or unclear, make your best educated guess based on wine industry knowledge.

Return the information in this JSON format:
{
  "wine_name": "extracted wine name",
  "winery": "producer/winery name", 
  "vintage": "year or null if not found",
  "region": "geographic region/appellation",
  "grape_varieties": "grape varieties as comma-separated string",
  "alcohol_content": "ABV percentage or null",
  "wine_type": "Red/White/Rosé/Sparkling",
  "additional_info": "any other relevant details",
  "confidence": 0.85,
  "extracted_text": "all visible text from the label"
}

Analyze the image now and return only the JSON response:
"""
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """
        Fallback text parsing if JSON parsing fails.
        """
        # Simple text parsing as fallback
        lines = text.strip().split('\n')
        
        result = {
            "wine_name": "Unknown Wine",
            "winery": "",
            "vintage": None,
            "region": "",
            "grape_varieties": "",
            "alcohol_content": None,
            "wine_type": "",
            "additional_info": "",
            "confidence": 0.5,
            "extracted_text": text,
            "parsing_method": "text_fallback"
        }
        
        # Try to extract basic info from text
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for vintage (4-digit year)
            import re
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            if year_match and not result["vintage"]:
                result["vintage"] = year_match.group()
            
            # Look for ABV
            abv_match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
            if abv_match and not result["alcohol_content"]:
                result["alcohol_content"] = abv_match.group(1) + "%"
        
        return result
    
    def analyze_menu(self, base64_image: str, image_metadata: dict) -> Dict[str, Any]:
        """
        Analyze menu image using Gemini Vision API to extract food items.
        
        Args:
            base64_image: Base64 encoded menu image
            image_metadata: Image processing metadata
            
        Returns:
            Dict containing extracted menu items and restaurant info
        """
        try:
            # Create the prompt for menu analysis
            prompt = self._create_menu_analysis_prompt()
            
            # Prepare image for Gemini
            image_data = {
                'mime_type': 'image/jpeg',
                'data': base64_image
            }
            
            # Call Gemini Vision API with optimized settings for complex menus
            response = self.model.generate_content(
                [prompt, image_data],
                generation_config={
                    "temperature": 0.2,  # Lower temperature for more consistent parsing
                    "max_output_tokens": 4096,  # Increased for complex menus with many items
                }
            )
            
            # Parse the response
            raw_text = response.text
            logger.info(f"Menu analysis raw output: {raw_text}")
            
            # Try to parse as JSON, fall back to text parsing
            try:
                parsed_result = parse_json_from_text(raw_text)
            except Exception as e:
                logger.warning(f"JSON parsing failed, using text parsing: {e}")
                parsed_result = self._parse_menu_text_response(raw_text)
            
            # Add metadata
            parsed_result['image_metadata'] = image_metadata
            parsed_result['analysis_method'] = 'gemini_vision_menu'
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"Menu analysis failed: {e}")
            raise GeminiApiError(f"Menu analysis failed: {str(e)}")
    
    def _create_menu_analysis_prompt(self) -> str:
        """
        Create detailed prompt for menu analysis.
        """
        return """
You are a culinary expert analyzing a restaurant menu image. Extract all menu items and return the information in JSON format.

Focus on extracting:
1. **Restaurant Info**: Name, cuisine style if visible
2. **Menu Items**: For each dish, identify:
   - Dish name (or create descriptive name from ingredients if none given)
   - Category (appetizer, main course, dessert, etc.)
   - Price if visible
   - Key ingredients listed
   - Protein type (beef, chicken, fish, vegetarian, etc.)
   - Cooking method (grilled, braised, fried, raw, etc.)
   - Cuisine style (Italian, French, Asian, etc.)
   - Flavor profile hints (spicy, rich, light, acidic, etc.)

Handle all menu formats:
- Formal dish names with descriptions
- Simple ingredient lists without formal names
- Mixed formats
- Multiple languages

Return in this JSON format:
{
  "restaurant_name": "name if visible or null",
  "cuisine_style": "overall cuisine type",
  "menu_items": [
    {
      "dish_name": "extracted or inferred dish name",
      "category": "appetizer/main/dessert/beverage",
      "price": "price if visible or null",
      "ingredients": ["list", "of", "key", "ingredients"],
      "protein": "main protein type or vegetarian",
      "cooking_method": "primary cooking method",
      "cuisine_type": "specific cuisine style for this dish",
      "flavor_profile": ["flavor", "characteristics"],
      "description": "full menu description if available"
    }
  ],
  "confidence": 0.85,
  "extracted_text": "all visible text from menu"
}

Analyze the menu image now and return only the JSON response:
"""
    
    def _parse_menu_text_response(self, text: str) -> Dict[str, Any]:
        """
        Fallback text parsing for menu analysis if JSON parsing fails.
        """
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        result = {
            "restaurant_name": None,
            "cuisine_style": "Unknown",
            "menu_items": [],
            "confidence": 0.4,
            "extracted_text": text,
            "parsing_method": "text_fallback"
        }
        
        # Simple parsing - each non-empty line becomes a menu item
        for line in lines:
            if len(line) > 3:  # Skip very short lines
                # Extract price if present
                import re
                price_match = re.search(r'\$\d+(?:\.\d{2})?', line)
                price = price_match.group() if price_match else None
                
                # Remove price from dish name
                dish_name = re.sub(r'\s*\$\d+(?:\.\d{2})?\s*', '', line).strip()
                
                menu_item = {
                    "dish_name": dish_name,
                    "category": "main",  # Default category
                    "price": price,
                    "ingredients": dish_name.split(', ') if ',' in dish_name else [dish_name],
                    "protein": "unknown",
                    "cooking_method": "unknown",
                    "cuisine_type": "unknown",
                    "flavor_profile": [],
                    "description": line
                }
                result["menu_items"].append(menu_item)
        
        return result

    def extract_text_only(self, base64_image: str) -> str:
        """
        Simple text extraction from image (OCR functionality).
        """
        try:
            prompt = "Extract and return all visible text from this image. Return only the text, no explanations."
            
            image_data = {
                'mime_type': 'image/jpeg',
                'data': base64_image
            }
            
            response = self.model.generate_content(
                [prompt, image_data],
                generation_config={"temperature": 0.1}
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise GeminiApiError(f"Text extraction failed: {str(e)}")