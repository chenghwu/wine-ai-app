import logging
import time
from typing import Dict, Any, List, Optional
from app.services.llm.gemini_engine import call_gemini_sync_with_retry
from app.utils.cache import cache_wine_recommendations, get_cached_wine_recommendations, generate_image_hash
from app.exceptions import GeminiApiError
from app.prompts.wine_pairing_prompts import (
    get_wine_pairing_prompt,
    get_food_text_analysis_prompt
)
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
        
        # For large menus (>6 items), use parallel batch processing directly for better performance
        if len(menu_items) > 6:
            try:
                recommendations = self._process_in_smaller_batches(menu_items)
            except Exception as e:
                logger.error(f"Parallel batch processing failed: {e}")
                try:
                    recommendations = self._recommend_for_batch_items(menu_items)
                except Exception as e2:
                    logger.error(f"Batch processing failed: {e2}")
                    recommendations = self._fallback_individual_processing(menu_items)
        else:
            # For smaller menus (≤6 items), use regular batch processing
            try:
                recommendations = self._recommend_for_batch_items(menu_items)
            except Exception as e:
                logger.error(f"Batch processing failed: {e}")
                recommendations = self._fallback_individual_processing(menu_items)
        
        # Cache the results
        cache_wine_recommendations(menu_hash, recommendations, ttl_minutes=15)
        
        return recommendations
    
    def _recommend_for_batch_items(self, menu_items: List[Dict]) -> Dict[str, Any]:
        """
        Process all menu items in a single batch API call for better performance.
        """
        # Create comprehensive batch prompt
        batch_prompt = self._create_batch_pairing_prompt(menu_items)
        
        try:
            # Single API call for all items with optimized settings for complex menus
            import time
            start_time = time.time()
            logger.info(f"Starting batch Gemini API call for {len(menu_items)} items")
            
            response = call_gemini_sync_with_retry(
                batch_prompt, 
                temperature=0.1,  # Lower temperature for faster, more deterministic responses
                max_retries=2,  # Fewer retries but more reliable parsing
                delay_seconds=0.5
            )
            
            api_duration = time.time() - start_time
            logger.info(f"Batch Gemini API call completed in {api_duration:.2f}s for {len(menu_items)} items")
            
            # Parse batch response
            recommendations = self._parse_batch_recommendation_response(response, menu_items)
            
            return recommendations
            
        except GeminiApiError as e:
            logger.error(f"Batch Gemini API error: {e}")
            raise e
    
    def _process_in_smaller_batches(self, menu_items: List[Dict]) -> Dict[str, Any]:
        """
        Process menu items in smaller batches (3-4 items each) with parallel processing for better performance.
        """
        import asyncio
        import concurrent.futures
        from threading import Thread
        from app.utils.env import setup_gemini_env
        
        batch_size = 3  # Optimal size - faster generation with good parallelism
        all_recommendations = {
            "menu_items": [],
            "overall_recommendations": [],
            "analysis_method": "ai_pairing_parallel_batch"
        }
        
        # Create batches
        batches = [menu_items[i:i + batch_size] for i in range(0, len(menu_items), batch_size)]
        logger.info(f"Processing {len(menu_items)} items in {len(batches)} parallel batches of size {batch_size}")
        
        def process_single_batch(batch_data):
            """Process a single batch in a separate thread"""
            batch_index, batch = batch_data
            try:
                logger.info(f"Starting parallel batch {batch_index + 1} with {len(batch)} items")
                start_time = time.time()
                
                batch_result = self._recommend_for_batch_items(batch)
                
                duration = time.time() - start_time
                logger.info(f"Completed parallel batch {batch_index + 1} in {duration:.2f}s")
                
                return batch_result
            except Exception as e:
                logger.error(f"Batch {batch_index + 1} failed: {e}")
                # Fall back to individual processing for this batch
                individual_results = {"menu_items": [], "overall_recommendations": []}
                for item in batch:
                    try:
                        item_recommendations = self._recommend_for_single_item(item)
                        individual_results["menu_items"].append({
                            "dish": item,
                            "wine_pairings": item_recommendations
                        })
                    except Exception as item_e:
                        logger.error(f"Item processing failed: {item_e}")
                        individual_results["menu_items"].append({
                            "dish": item,
                            "wine_pairings": self._get_fallback_recommendations(item)
                        })
                return individual_results
        
        # Process batches in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, len(batches))) as executor:
            batch_data = [(i, batch) for i, batch in enumerate(batches)]
            results = list(executor.map(process_single_batch, batch_data))
        
        # Merge all results
        for batch_result in results:
            all_recommendations["menu_items"].extend(batch_result.get("menu_items", []))
            
            # Merge overall recommendations (avoid duplicates)
            existing_categories = {rec.get("category", "") for rec in all_recommendations["overall_recommendations"]}
            new_recommendations = [
                rec for rec in batch_result.get("overall_recommendations", [])
                if rec.get("category", "") not in existing_categories
            ]
            all_recommendations["overall_recommendations"].extend(new_recommendations)
        
        # Generate overall recommendations if none were created
        if not all_recommendations["overall_recommendations"]:
            all_recommendations["overall_recommendations"] = self._generate_overall_recommendations(menu_items)
        
        return all_recommendations
    
    
    def _fallback_individual_processing(self, menu_items: List[Dict]) -> Dict[str, Any]:
        """
        Fallback to individual processing if batch fails.
        """
        recommendations = {
            "menu_items": [],
            "overall_recommendations": [],
            "analysis_method": "ai_pairing_individual"
        }
        
        for item in menu_items:
            # Check for individual item cache
            item_hash = self._generate_item_hash(item)
            cached_item_recommendations = get_cached_wine_recommendations(f"item_{item_hash}")
            
            if cached_item_recommendations:
                # Extract wine_pairings from cached format
                cached_pairings = cached_item_recommendations.get("menu_items", [{}])[0].get("wine_pairings", {})
                recommendations["menu_items"].append({
                    "dish": item,
                    "wine_pairings": cached_pairings
                })
                continue
            
            try:
                item_recommendations = self._recommend_for_single_item(item)
                recommendations["menu_items"].append({
                    "dish": item,
                    "wine_pairings": item_recommendations
                })
                
                # Cache individual item recommendations
                item_cache_data = {
                    "menu_items": [{
                        "dish": item,
                        "wine_pairings": item_recommendations
                    }],
                    "analysis_method": "ai_pairing_individual_cached"
                }
                cache_wine_recommendations(f"item_{item_hash}", item_cache_data, ttl_minutes=30)
                
            except Exception as e:
                logger.warning(f"Failed to generate recommendations for {item.get('dish_name', 'unknown')}: {e}")
                # Add fallback recommendations
                recommendations["menu_items"].append({
                    "dish": item,
                    "wine_pairings": self._get_fallback_recommendations(item)
                })
        
        # Generate overall menu recommendations (cached for performance)
        overall_hash = f"overall_{self._generate_menu_hash(menu_items)}"
        cached_overall = get_cached_wine_recommendations(overall_hash)
        
        if cached_overall and cached_overall.get("overall_recommendations"):
            recommendations["overall_recommendations"] = cached_overall["overall_recommendations"]
        else:
            recommendations["overall_recommendations"] = self._generate_overall_recommendations(menu_items)
            # Cache just the overall recommendations separately
            overall_cache_data = {
                "overall_recommendations": recommendations["overall_recommendations"],
                "analysis_method": "overall_cached"
            }
            cache_wine_recommendations(overall_hash, overall_cache_data, ttl_minutes=60)
        
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
        Create a detailed prompt for wine pairing recommendations using unified prompt function.
        """
        return get_wine_pairing_prompt(menu_item, format_type="text")
    
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
        
        # Pattern: [Year] [Producer] [Wine Name] ([Grape Variety]) - [Region] ($[price])
        pattern = r'(\d{4})?\s*(.+?)\s*\(([^)]+)\)\s*-\s*(.+?)\s*\(\$(\d+(?:-\d+)?)\)'
        match = re.search(pattern, line)
        
        if match:
            vintage, wine_info, grape_variety, region, price_range = match.groups()
            
            return {
                "wine_name": wine_info.strip(),
                "grape_variety": grape_variety.strip(),
                "vintage": vintage or "NV",
                "region": region.strip(),
                "price_range": f"${price_range}",
                "confidence": 0.85,
                "recommendation_type": "specific"
            }
        
        # Fallback pattern without grape variety: [Year] [Producer] [Wine Name] - [Region] ($[price])
        pattern_fallback = r'(\d{4})?\s*(.+?)\s*-\s*(.+?)\s*\(\$(\d+(?:-\d+)?)\)'
        match_fallback = re.search(pattern_fallback, line)
        
        if match_fallback:
            vintage, wine_info, region, price_range = match_fallback.groups()
            
            return {
                "wine_name": wine_info.strip(),
                "grape_variety": None,
                "vintage": vintage or "NV",
                "region": region.strip(),
                "price_range": f"${price_range}",
                "confidence": 0.85,
                "recommendation_type": "specific"
            }
        
        # Fallback parsing
        return {
            "wine_name": line.split('-')[0].strip() if '-' in line else line.strip(),
            "grape_variety": None,
            "vintage": "NV",
            "region": "Various",
            "price_range": "US$25-50",
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
                        "grape_variety": "Cabernet Sauvignon",
                        "vintage": "2020",
                        "region": "Napa Valley, CA",
                        "price_range": "US$30-50",
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
                        "grape_variety": "Sauvignon Blanc",
                        "vintage": "2022",
                        "region": "Loire Valley, France",
                        "price_range": "US$20-35",
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
                        "grape_variety": "Pinot Noir",
                        "vintage": "2021",
                        "region": "Oregon, USA",
                        "price_range": "US$25-40",
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
    
    def _generate_item_hash(self, menu_item: Dict) -> str:
        """
        Generate a consistent hash for a single menu item to use for individual caching.
        """
        dish_name = menu_item.get('dish_name', '')
        protein = menu_item.get('protein', '')
        cooking_method = menu_item.get('cooking_method', '')
        cuisine_type = menu_item.get('cuisine_type', '')
        item_string = f"{dish_name}|{protein}|{cooking_method}|{cuisine_type}"
        
        return hashlib.sha256(item_string.encode()).hexdigest()[:12]
    
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
                                "grape_variety": "Pinot Noir",
                                "vintage": "2019",
                                "region": "Willamette Valley, Oregon",
                                "price_range": "US$35-45",
                                "reasoning": "Oregon Pinot's bright acidity and cherry notes complement duck's richness",
                                "confidence": 0.92
                            },
                            {
                                "wine_name": "Château de Beaucastel Châteauneuf-du-Pape",
                                "grape_variety": "Grenache Blend",
                                "vintage": "2018",
                                "region": "Southern Rhône, France",
                                "price_range": "US$65-85",
                                "reasoning": "Complex Rhône blend with earthy depth and spice complements duck's richness",
                                "confidence": 0.88
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
                            },
                            {
                                "grape_variety": "Syrah",
                                "regions": ["Northern Rhône", "Australia", "Washington State"],
                                "wine_style": "Full-bodied red with spice and structure",
                                "characteristics": ["Dark fruit", "Black pepper", "Smoky notes"],
                                "reasoning": "Bold flavors and spice complement rich duck preparation",
                                "confidence": 0.85
                            },
                            {
                                "grape_variety": "Châteauneuf-du-Pape Blend",
                                "regions": ["Southern Rhône", "California", "Australia"],
                                "wine_style": "Full-bodied red blend with complexity",
                                "characteristics": ["Herbal notes", "Rich fruit", "Structured tannins"],
                                "reasoning": "Complex wine matches the complexity of duck with rich sauces",
                                "confidence": 0.82
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
    
    def _create_batch_pairing_prompt(self, menu_items: List[Dict]) -> str:
        """
        Create a comprehensive prompt for batch wine pairing using unified prompt function.
        """
        return get_wine_pairing_prompt(menu_items, format_type="json")
    
    def _parse_batch_recommendation_response(self, response: str, menu_items: List[Dict]) -> Dict[str, Any]:
        """
        Parse the batch recommendation response from Gemini.
        """
        try:
            # Try to parse JSON response
            import json
            import re
            
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed_response = json.loads(json_str)
            else:
                parsed_response = json.loads(response)
            
            # Convert to expected format
            recommendations = {
                "menu_items": [],
                "overall_recommendations": parsed_response.get("overall_recommendations", []),
                "analysis_method": "ai_pairing_batch"
            }
            
            # Map dish indices back to original menu items
            batch_items = parsed_response.get("menu_items", [])
            
            for i, original_item in enumerate(menu_items):
                # Find corresponding recommendation by dish_index
                matching_rec = None
                for batch_item in batch_items:
                    if batch_item.get("dish_index") == i + 1:
                        matching_rec = batch_item
                        break
                
                if matching_rec:
                    recommendations["menu_items"].append({
                        "dish": original_item,
                        "wine_pairings": matching_rec.get("wine_pairings", {})
                    })
                else:
                    # Fallback if no matching recommendation found
                    recommendations["menu_items"].append({
                        "dish": original_item,
                        "wine_pairings": self._get_fallback_recommendations(original_item)
                    })
            
            return recommendations
            
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.error(f"Failed to parse batch response: {e}")
            
            # Fallback to basic recommendations for each item
            recommendations = {
                "menu_items": [
                    {
                        "dish": item,
                        "wine_pairings": self._get_fallback_recommendations(item)
                    }
                    for item in menu_items
                ],
                "overall_recommendations": [{
                    "category": "Balanced Selection",
                    "recommendation": "Mix of medium-bodied reds and crisp whites",
                    "reasoning": "Safe pairing approach for diverse menu (batch parsing failed)"
                }],
                "analysis_method": "fallback_batch_error"
            }
            
            return recommendations