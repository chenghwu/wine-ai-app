"""
Wine pairing prompts for menu analysis and food-to-wine recommendations.
Centralized prompt management with unified prompt generation.
"""
from typing import List, Dict, Union

def get_wine_pairing_prompt(
    menu_items: Union[Dict, List[Dict]], 
    format_type: str = "text"
) -> str:
    """
    Create wine pairing prompt for single dish or multiple dishes.
    
    Args:
        menu_items: Single menu item dict or list of menu item dicts
        format_type: "text" for single dish text format, "json" for batch JSON format
        
    Returns:
        Formatted prompt string for AI wine pairing analysis
    """
    # Normalize to list for consistent processing
    if isinstance(menu_items, dict):
        items_list = [menu_items]
        is_single_item = True
    else:
        items_list = menu_items
        is_single_item = len(items_list) == 1
    
    # For single item and text format, use the structured text format
    if is_single_item and format_type == "text":
        return _get_single_dish_text_prompt(items_list[0])
    
    # For multiple items or JSON format requested, use batch JSON format
    return _get_batch_json_prompt(items_list)


def _get_single_dish_text_prompt(menu_item: Dict) -> str:
    """Generate structured text prompt for single dish analysis."""
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

1. **Specific Wine Recommendations** (MINIMUM 2 wines, up to 3):
   - Actual wines with producer, vintage, region, and grape variety
   - Price range estimate in USD
   - Detailed pairing explanation

2. **General Wine Categories** (EXACTLY 3 categories):
   - Grape variety and wine style (provide broader guidance beyond specific bottles)
   - Multiple regional options to give variety of choices
   - Key characteristics that make this category work with the dish
   - General pairing principles that apply to this wine category

Format your response as:

**SPECIFIC RECOMMENDATIONS:**
1. [Year] [Producer] [Wine Name] ([Grape Variety]) - [Region] (US$[price range])
   Reasoning: [detailed explanation of why this pairing works]

2. [Year] [Producer] [Wine Name] ([Grape Variety]) - [Region] (US$[price range])
   Reasoning: [detailed explanation]

3. [Year] [Producer] [Wine Name] ([Grape Variety]) - [Region] (US$[price range]) [OPTIONAL THIRD RECOMMENDATION]
   Reasoning: [detailed explanation]

**GENERAL CATEGORIES:**
1. **[Grape Variety]** from [Multiple Regions]
   Style: [wine style description - light/medium/full-bodied, dry/off-dry, etc.]
   Characteristics: [key characteristics to look for - acidity, tannins, fruit profile]
   Pairing Logic: [general principles why this category works with the dish type]

2. **[Grape Variety]** from [Multiple Regions]
   Style: [wine style description]
   Characteristics: [key characteristics to look for]
   Pairing Logic: [general principles for this category and dish combination]

3. **[Grape Variety]** from [Multiple Regions]
   Style: [wine style description]
   Characteristics: [key characteristics to look for]
   Pairing Logic: [general principles for this category]

Focus on classic wine pairing principles: complement or contrast flavors, match wine weight to food weight, consider acidity, tannins, and serving temperature. 

IMPORTANT: Ensure consistency between specific wines and general categories - at least ONE general category should match a grape variety from your specific recommendations. For example, if you recommend specific Pinot Noir wines, include Pinot Noir as one of the general categories.
""".strip()


def _get_batch_json_prompt(menu_items: List[Dict]) -> str:
    """Generate JSON batch prompt for multiple dishes."""
    prompt = """Expert sommelier: analyze menu, provide wine pairings. Return valid JSON.

MENU:
"""
    
    # Add each menu item with details
    for i, item in enumerate(menu_items, 1):
        dish_name = item.get('dish_name', 'Unknown Dish')
        protein = item.get('protein', 'unknown')
        cooking_method = item.get('cooking_method', 'unknown')
        cuisine_type = item.get('cuisine_type', 'unknown')
        flavor_profile = item.get('flavor_profile', [])
        ingredients = item.get('ingredients', [])
        price = item.get('price', '')
        description = item.get('description', '')
        
        prompt += f"""
{i}. {dish_name}
   Protein: {protein} | Method: {cooking_method} | Cuisine: {cuisine_type}
   Flavors: {', '.join(flavor_profile) if flavor_profile else 'unknown'}
   Ingredients: {', '.join(ingredients[:4]) if ingredients else 'unknown'}
"""

    prompt += """

JSON format:
{
  "menu_items": [
    {
      "dish_index": 1,
      "wine_pairings": {
        "specific_recommendations": [
          {
            "wine_name": "Wine name",
            "grape_variety": "Grape",
            "vintage": "Year",
            "region": "Region",
            "price_range": "US$XX-YY",
            "reasoning": "Why this wine pairs with this dish",
            "confidence": 0.85
          }
        ],
        "general_recommendations": [
          {
            "grape_variety": "Same as one of the specific wines above",
            "regions": ["region1", "region2"],
            "wine_style": "Style description",
            "characteristics": ["char1", "char2"],
            "reasoning": "Why this category works"
          },
          {
            "grape_variety": "Alternative variety",
            "regions": ["region3", "region4"],
            "wine_style": "Different style",
            "characteristics": ["char3", "char4"],
            "reasoning": "Why this alternative works"
          }
        ]
      }
    }
  ],
  "overall_recommendations": [
    {
      "category": "Category",
      "recommendation": "Recommendation",
      "reasoning": "Analysis"
    }
  ]
}

Requirements: 
- 2+ specific wines, 3 general categories per dish
- IMPORTANT: At least ONE general category must match a grape variety from the specific recommendations 
- General categories should build upon the specific wines (if recommending Pinot Noir specifically, include Pinot Noir as a general category)
- Focus on pairing principles and detailed reasoning
- Return JSON only."""
    
    return prompt


def get_food_text_analysis_prompt(food_description: str) -> str:
    """
    Create a prompt for analyzing text-based food descriptions for wine pairing.
    
    Args:
        food_description: User's text description of food/dish
        
    Returns:
        Formatted prompt for food analysis
    """
    return f"""
As an expert sommelier, analyze this food description and provide wine pairing recommendations:

**Food Description**: {food_description}

First, analyze the food to understand:
- Main protein or key ingredient
- Likely cooking method
- Flavor intensity and profile
- Cuisine style (if identifiable)

Then provide wine recommendations in two categories:

1. **Specific Wine Recommendations** (MINIMUM 2, up to 3):
   - Actual wines with producer, vintage, region
   - Price range estimate in USD
   - Detailed pairing explanation

2. **General Wine Categories** (MINIMUM 2, up to 3):
   - Grape variety and style
   - Recommended regions
   - Key characteristics to look for
   - Why this category works

Format your response clearly with reasoning for each recommendation.
Focus on classic pairing principles: complement or contrast flavors, match wine weight to food weight.
""".strip()