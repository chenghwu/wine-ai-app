import pytest
from app.constants.food_base_categories import FOOD_BASE_CATEGORIES


class TestFoodBaseCategories:
    
    def test_food_base_categories_structure(self):
        assert isinstance(FOOD_BASE_CATEGORIES, dict)
        assert len(FOOD_BASE_CATEGORIES) > 0
        
        for category, examples in FOOD_BASE_CATEGORIES.items():
            assert isinstance(category, str)
            assert isinstance(examples, list)
            assert category != ""
    
    def test_required_categories_exist(self):
        required_categories = [
            "Beef", "Pork", "Lamb", "Game", "Poultry", "Fish", 
            "Shellfish", "Seafood", "Vegetables", "Cheese", 
            "Grains & Pasta", "Bread & Pastry", "Legumes", 
            "Fruits", "Nuts", "Dessert", "Spicy / Asian", 
            "Sauces & Condiments", "Other"
        ]
        
        for category in required_categories:
            assert category in FOOD_BASE_CATEGORIES, f"Missing required category: {category}"
    
    def test_other_category_exists_and_empty(self):
        assert "Other" in FOOD_BASE_CATEGORIES
        assert FOOD_BASE_CATEGORIES["Other"] == []
    
    def test_beef_category_examples(self):
        beef_examples = FOOD_BASE_CATEGORIES["Beef"]
        assert len(beef_examples) > 0
        
        expected_items = ["grilled ribeye steak", "braised brisket", "beef tenderloin"]
        for item in expected_items:
            assert any(item in example.lower() for example in beef_examples)
    
    def test_seafood_category_examples(self):
        seafood_examples = FOOD_BASE_CATEGORIES["Seafood"]
        assert len(seafood_examples) > 0
        
        expected_items = ["seafood paella", "bouillabaisse", "cioppino"]
        for item in expected_items:
            assert any(item in example.lower() for example in seafood_examples)
    
    def test_cheese_category_examples(self):
        cheese_examples = FOOD_BASE_CATEGORIES["Cheese"]
        assert len(cheese_examples) > 0
        
        expected_items = ["brie", "cheddar", "gorgonzola", "blue cheese"]
        for item in expected_items:
            assert any(item in example.lower() for example in cheese_examples)
    
    def test_game_category_includes_foie_gras(self):
        game_examples = FOOD_BASE_CATEGORIES["Game"]
        foie_gras_items = ["foie gras", "foie gras terrine", "seared foie gras"]
        
        for item in foie_gras_items:
            assert any(item in example.lower() for example in game_examples)
    
    def test_spicy_asian_category_examples(self):
        spicy_examples = FOOD_BASE_CATEGORIES["Spicy / Asian"]
        assert len(spicy_examples) > 0
        
        expected_items = ["pad thai", "szechuan", "kimchi", "curry"]
        for item in expected_items:
            assert any(item in example.lower() for example in spicy_examples)
    
    def test_no_empty_categories_except_other(self):
        for category, examples in FOOD_BASE_CATEGORIES.items():
            if category != "Other":
                assert len(examples) > 0, f"Category '{category}' should not be empty"
    
    def test_examples_are_strings(self):
        for category, examples in FOOD_BASE_CATEGORIES.items():
            for example in examples:
                assert isinstance(example, str), f"Example in '{category}' is not a string: {example}"
                assert example.strip() != "", f"Empty string found in '{category}'"
    
    def test_categories_case_sensitivity(self):
        for category in FOOD_BASE_CATEGORIES.keys():
            assert category[0].isupper(), f"Category '{category}' should start with uppercase"
    
    def test_specific_food_items_categorized_correctly(self):
        assert "grilled salmon fillet" in FOOD_BASE_CATEGORIES["Fish"]
        assert "lobster thermidor" in FOOD_BASE_CATEGORIES["Shellfish"]
        assert "dark chocolate mousse" in FOOD_BASE_CATEGORIES["Dessert"]
        assert "truffle aioli" in FOOD_BASE_CATEGORIES["Sauces & Condiments"]
        assert "roasted lamb shank" in FOOD_BASE_CATEGORIES["Lamb"]