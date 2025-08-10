import logging
from typing import Dict, Any, List, Optional
from app.services.llm.gemini_engine import call_gemini_sync_with_retry
from app.utils.cache import cache_wine_recommendations, get_cached_wine_recommendations, generate_image_hash
from app.exceptions import GeminiApiError
import hashlib

logger = logging.getLogger(__name__)

class WineRecommender:
    """
    Generate wine recommendations for food items using AI and wine pairing principles.
    Provides both specific wine recommendations and general wine categories.
    """
    
    def __init__(self):
        pass
    
    def recommend_wines_for_menu(self, menu_items: List[Dict], use_mock: bool = False) -> Dict[str, Any]:
        """
        Generate wine recommendations for a list of menu items.
        
        Args:
            menu_items: List of parsed menu items from menu analysis
            use_mock: Whether to return mock recommendations for development
            
        Returns:
            Dict containing wine recommendations for each menu item
        """
        if use_mock:
            return self._get_mock_recommendations()
        
        # Generate cache key based on menu items
        menu_hash = self._generate_menu_hash(menu_items)
        
        # Check cache first
        cached_recommendations = get_cached_wine_recommendations(menu_hash)
        if cached_recommendations:
            logger.info(f"Using cached wine recommendations: {menu_hash}")
            return cached_recommendations
        
        recommendations = {
            "menu_items": [],
            "overall_recommendations": [],
            "analysis_method": "ai_pairing"
        }
        
        for item in menu_items:
            try:
                item_recommendations = self._recommend_for_single_item(item)
                recommendations["menu_items"].append({
                    "dish": item,
                    "wine_pairings": item_recommendations
                })
            except Exception as e:
                logger.warning(f"Failed to generate recommendations for {item.get('dish_name', 'unknown')}: {e}")
                # Add fallback recommendations
                recommendations["menu_items"].append({
                    "dish": item,
                    "wine_pairings": self._get_fallback_recommendations(item)
                })
        
        # Generate overall menu recommendations
        recommendations["overall_recommendations"] = self._generate_overall_recommendations(menu_items)
        
        # Cache the results
        cache_wine_recommendations(menu_hash, recommendations, ttl_minutes=15)
        
        return recommendations
    
    def _recommend_for_single_item(self, menu_item: Dict) -> Dict[str, Any]:
        """
        Generate wine recommendations for a single menu item.
        """
        # Create detailed prompt for wine pairing
        prompt = self._create_pairing_prompt(menu_item)
        
        try:
            # Use Gemini to generate recommendations
            response = call_gemini_sync_with_retry(prompt, temperature=0.3)
            
            # Parse the response (expecting structured recommendations)
            parsed_recommendations = self._parse_recommendation_response(response, menu_item)
            
            return parsed_recommendations
            
        except GeminiApiError as e:
            logger.error(f"Gemini API error for item {menu_item.get('dish_name')}: {e}")
            return self._get_fallback_recommendations(menu_item)
    
    def _create_pairing_prompt(self, menu_item: Dict) -> str:
        """
        Create a detailed prompt for wine pairing recommendations.
        """
        dish_name = menu_item.get('dish_name', 'Unknown Dish')
        protein = menu_item.get('protein', 'unknown')
        cooking_method = menu_item.get('cooking_method', 'unknown')
        cuisine_type = menu_item.get('cuisine_type', 'unknown')
        flavor_profile = menu_item.get('flavor_profile', [])
        ingredients = menu_item.get('ingredients', [])
        
        return f"""
As a sommelier expert, recommend wines for this dish:

**Dish**: {dish_name}
**Protein**: {protein}
**Cooking Method**: {cooking_method}
**Cuisine**: {cuisine_type}
**Key Ingredients**: {', '.join(ingredients)}
**Flavor Profile**: {', '.join(flavor_profile)}

Provide recommendations in two tiers:

1. **Specific Wine Recommendations** (2-3 wines):
   - Actual wines with producer, vintage, region
   - Price range estimate
   - Detailed pairing explanation

2. **General Wine Categories** (2-3 categories):
   - Grape variety and style
   - Recommended regions
   - Key characteristics to look for
   - Why this category works

Format your response as:

**SPECIFIC RECOMMENDATIONS:**
1. [Year] [Producer] [Wine Name] - [Region] ($[price range])
   Reasoning: [detailed explanation of why this pairing works]

2. [Year] [Producer] [Wine Name] - [Region] ($[price range])
   Reasoning: [detailed explanation]

**GENERAL CATEGORIES:**
1. **[Grape Variety]** from [Regions]
   Style: [wine style description]
   Characteristics: [key wine characteristics]
   Pairing Logic: [why this works with the dish]

2. **[Grape Variety]** from [Regions]
   Style: [wine style description]
   Characteristics: [key wine characteristics]
   Pairing Logic: [why this works with the dish]

Focus on classic wine pairing principles: complement or contrast flavors, match wine weight to food weight, consider acidity, tannins, and serving temperature.
"""
    
    def _parse_recommendation_response(self, response: str, menu_item: Dict) -> Dict[str, Any]:
        """
        Parse the AI response into structured wine recommendations.
        """
        # Simple parsing of the structured response
        specific_recommendations = []
        general_recommendations = []
        
        lines = response.split('\n')
        current_section = None
        current_item = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if '**SPECIFIC RECOMMENDATIONS:**' in line:
                current_section = 'specific'
                continue
            elif '**GENERAL CATEGORIES:**' in line:
                current_section = 'general'
                continue
            
            if current_section == 'specific' and line.startswith(('1.', '2.', '3.')):
                # Parse specific wine recommendation
                wine_match = self._parse_specific_wine(line)
                if wine_match:
                    specific_recommendations.append(wine_match)
            
            elif current_section == 'general' and line.startswith(('1.', '2.', '3.')):
                # Parse general category recommendation
                category_match = self._parse_general_category(line)
                if category_match:
                    general_recommendations.append(category_match)
            
            elif line.startswith('Reasoning:') or line.startswith('Pairing Logic:'):
                # Add reasoning to the last recommendation
                reasoning = line.replace('Reasoning:', '').replace('Pairing Logic:', '').strip()
                if current_section == 'specific' and specific_recommendations:
                    specific_recommendations[-1]['reasoning'] = reasoning
                elif current_section == 'general' and general_recommendations:
                    general_recommendations[-1]['reasoning'] = reasoning
        
        return {
            "specific_recommendations": specific_recommendations,
            "general_recommendations": general_recommendations,
            "confidence": 0.85 if specific_recommendations and general_recommendations else 0.6
        }
    
    def _parse_specific_wine(self, line: str) -> Optional[Dict]:
        """
        Parse a specific wine recommendation line.
        """
        import re
        
        # Pattern: [Year] [Producer] [Wine Name] - [Region] ($[price])
        pattern = r'(\d{4})?\s*(.+?)\s*-\s*(.+?)\s*\(\$(\d+(?:-\d+)?)\)'
        match = re.search(pattern, line)
        
        if match:
            vintage, wine_info, region, price_range = match.groups()
            
            return {
                "wine_name": wine_info.strip(),
                "vintage": vintage or "NV",
                "region": region.strip(),
                "price_range": f"${price_range}",
                "confidence": 0.85,
                "recommendation_type": "specific"
            }
        
        # Fallback parsing
        return {
            "wine_name": line.split('-')[0].strip() if '-' in line else line.strip(),
            "vintage": "NV",
            "region": "Various",
            "price_range": "$25-50",
            "confidence": 0.6,
            "recommendation_type": "specific"
        }
    
    def _parse_general_category(self, line: str) -> Optional[Dict]:
        """
        Parse a general wine category recommendation.
        """
        # Extract grape variety and region from formatted line
        import re
        
        # Pattern: **[Grape Variety]** from [Regions]
        pattern = r'\*\*(.+?)\*\*\s*from\s*(.+)'
        match = re.search(pattern, line)
        
        if match:
            grape_variety, regions = match.groups()
            return {
                "grape_variety": grape_variety.strip(),
                "regions": [r.strip() for r in regions.split(',')],
                "wine_style": "Medium-bodied",  # Default, should be parsed from response
                "characteristics": [],  # Should be parsed from response
                "recommendation_type": "general",
                "confidence": 0.8
            }
        
        # Fallback parsing
        return {
            "grape_variety": line.split()[0] if line.split() else "Cabernet Sauvignon",
            "regions": ["Various"],
            "wine_style": "Medium-bodied",
            "characteristics": [],
            "recommendation_type": "general",
            "confidence": 0.6
        }
    
    def _get_fallback_recommendations(self, menu_item: Dict) -> Dict[str, Any]:
        """
        Provide basic wine recommendations when AI analysis fails.
        """
        protein = menu_item.get('protein', '').lower()
        
        # Basic pairing rules
        if 'beef' in protein or 'lamb' in protein:
            return {
                "specific_recommendations": [
                    {
                        "wine_name": "Cabernet Sauvignon",
                        "vintage": "2020",
                        "region": "Napa Valley, CA",
                        "price_range": "$30-50",
                        "reasoning": "Classic pairing for red meat - tannins complement protein",
                        "confidence": 0.7
                    }
                ],
                "general_recommendations": [
                    {
                        "grape_variety": "Cabernet Sauvignon",
                        "regions": ["Bordeaux", "Napa Valley", "Australia"],
                        "wine_style": "Full-bodied red",
                        "characteristics": ["High tannins", "Dark fruit", "Good structure"],
                        "reasoning": "Bold wines for bold flavors",
                        "confidence": 0.8
                    }
                ]
            }
        elif 'fish' in protein or 'seafood' in protein:
            return {
                "specific_recommendations": [
                    {
                        "wine_name": "Sauvignon Blanc",
                        "vintage": "2022",
                        "region": "Loire Valley, France",
                        "price_range": "$20-35",
                        "reasoning": "Crisp acidity complements delicate fish flavors",
                        "confidence": 0.7
                    }
                ],
                "general_recommendations": [
                    {
                        "grape_variety": "Sauvignon Blanc",
                        "regions": ["Loire Valley", "New Zealand", "California"],
                        "wine_style": "Crisp white",
                        "characteristics": ["High acidity", "Citrus notes", "Mineral finish"],
                        "reasoning": "Light wines for delicate proteins",
                        "confidence": 0.8
                    }
                ]
            }
        else:
            # Default recommendations
            return {
                "specific_recommendations": [
                    {
                        "wine_name": "Pinot Noir",
                        "vintage": "2021",
                        "region": "Oregon, USA",
                        "price_range": "$25-40",
                        "reasoning": "Versatile wine that pairs well with many dishes",
                        "confidence": 0.6
                    }
                ],
                "general_recommendations": [
                    {
                        "grape_variety": "Pinot Noir",
                        "regions": ["Burgundy", "Oregon", "California"],
                        "wine_style": "Light to medium-bodied red",
                        "characteristics": ["Bright acidity", "Red fruit", "Moderate tannins"],
                        "reasoning": "Food-friendly wine for various preparations",
                        "confidence": 0.7
                    }
                ]
            }
    
    def _generate_overall_recommendations(self, menu_items: List[Dict]) -> List[Dict]:
        """
        Generate overall wine recommendations for the entire menu.
        """
        # Analyze the overall menu style and suggest wine categories
        cuisine_types = [item.get('cuisine_type', '') for item in menu_items]
        proteins = [item.get('protein', '') for item in menu_items]
        
        # Simple analysis for overall recommendations
        overall_recs = []
        
        if any('french' in c.lower() for c in cuisine_types):
            overall_recs.append({
                "category": "French Wine Focus",
                "recommendation": "Burgundy Pinot Noir and Loire Valley whites",
                "reasoning": "Complement French cuisine with regional wines"
            })
        
        if any(p in ['beef', 'lamb'] for p in proteins):
            overall_recs.append({
                "category": "Bold Reds",
                "recommendation": "Cabernet Sauvignon, Malbec, or Rhône blends",
                "reasoning": "Strong tannins to match rich meat dishes"
            })
        
        if any(p in ['fish', 'seafood'] for p in proteins):
            overall_recs.append({
                "category": "Crisp Whites",
                "recommendation": "Sauvignon Blanc, Albariño, or Chablis",
                "reasoning": "Clean acidity to enhance seafood flavors"
            })
        
        return overall_recs or [{
            "category": "Balanced Selection",
            "recommendation": "Mix of medium-bodied reds and crisp whites",
            "reasoning": "Versatile wines for diverse menu"
        }]
    
    def _generate_menu_hash(self, menu_items: List[Dict]) -> str:
        """
        Generate a consistent hash for menu items to use for caching.
        """
        # Create a string representation of the menu items
        menu_string = ""
        for item in menu_items:
            dish_name = item.get('dish_name', '')
            protein = item.get('protein', '')
            cooking_method = item.get('cooking_method', '')
            menu_string += f"{dish_name}|{protein}|{cooking_method};"
        
        return hashlib.sha256(menu_string.encode()).hexdigest()[:16]
    
    def _get_mock_recommendations(self) -> Dict[str, Any]:
        """
        Return mock wine recommendations for development/testing.
        """
        return {
            "menu_items": [
                {
                    "dish": {
                        "dish_name": "Pan-Seared Duck Breast",
                        "protein": "duck",
                        "cooking_method": "pan-seared"
                    },
                    "wine_pairings": {
                        "specific_recommendations": [
                            {
                                "wine_name": "Domaine Drouhin Pinot Noir",
                                "vintage": "2019",
                                "region": "Willamette Valley, Oregon",
                                "price_range": "$35-45",
                                "reasoning": "Oregon Pinot's bright acidity and cherry notes complement duck's richness",
                                "confidence": 0.92
                            }
                        ],
                        "general_recommendations": [
                            {
                                "grape_variety": "Pinot Noir",
                                "regions": ["Burgundy", "Oregon", "Russian River"],
                                "wine_style": "Medium-bodied red with bright acidity",
                                "characteristics": ["Red fruit", "Earthy undertones", "Balanced tannins"],
                                "reasoning": "Classic duck pairing - acidity cuts fat, fruit complements gamey flavors",
                                "confidence": 0.88
                            }
                        ]
                    }
                }
            ],
            "overall_recommendations": [
                {
                    "category": "French-Style Wines",
                    "recommendation": "Burgundy and Loire Valley selections",
                    "reasoning": "Match French cooking techniques with regional wines"
                }
            ],
            "analysis_method": "mock_response"
        }