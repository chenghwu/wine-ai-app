import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.food_pairing import save_food_pairings, get_wine_and_pairings
from app.db.models.food_pairing import FoodPairingCategory, FoodPairingExample
from app.db.models.wine_summary import WineSummary


class TestFoodPairingCRUD:
    
    @pytest.mark.asyncio
    async def test_save_food_pairings_single_category(self):
        mock_session = AsyncMock()
        wine_id = 1
        
        data = [
            {
                "category": "Beef",
                "base_category": "Beef",
                "examples": [
                    {"food": "Grilled Steak", "reason": "Bold tannins match rich meat"},
                    {"food": "Braised Short Ribs", "reason": "Hearty wine complements slow-cooked beef"}
                ]
            }
        ]
        
        await save_food_pairings(mock_session, wine_id, data)
        
        assert mock_session.add.call_count == 3
        assert mock_session.flush.call_count == 1
        assert mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_save_food_pairings_multiple_categories(self):
        mock_session = AsyncMock()
        wine_id = 1
        
        data = [
            {
                "category": "Beef",
                "base_category": "Beef",
                "examples": [
                    {"food": "Grilled Steak", "reason": "Bold tannins match rich meat"}
                ]
            },
            {
                "category": "Aged Cheese",
                "base_category": "Cheese",
                "examples": [
                    {"food": "Aged Cheddar", "reason": "Complements wine's acidity"},
                    {"food": "Blue Cheese", "reason": "Strong flavors pair well"}
                ]
            }
        ]
        
        await save_food_pairings(mock_session, wine_id, data)
        
        assert mock_session.add.call_count == 5
        assert mock_session.flush.call_count == 2
        assert mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_save_food_pairings_empty_examples(self):
        mock_session = AsyncMock()
        wine_id = 1
        
        data = [
            {
                "category": "Vegetables",
                "base_category": "Vegetables", 
                "examples": []
            }
        ]
        
        await save_food_pairings(mock_session, wine_id, data)
        
        assert mock_session.add.call_count == 1
        assert mock_session.flush.call_count == 1
        assert mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_get_wine_and_pairings_found(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock(spec=WineSummary)
        mock_wine.food_pairing_categories = [
            MagicMock(spec=FoodPairingCategory),
            MagicMock(spec=FoodPairingCategory)
        ]
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_wine
        mock_session.execute.return_value = mock_result
        
        wine, categories = await get_wine_and_pairings(mock_session, wine_name)
        
        assert wine == mock_wine
        assert len(categories) == 2
        assert mock_session.execute.called
    
    @pytest.mark.asyncio
    async def test_get_wine_and_pairings_not_found(self):
        mock_session = AsyncMock()
        wine_name = "Nonexistent Wine"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        wine, categories = await get_wine_and_pairings(mock_session, wine_name)
        
        assert wine is None
        assert categories == []
        assert mock_session.execute.called
    
    @pytest.mark.asyncio
    async def test_get_wine_and_pairings_no_categories(self):
        mock_session = AsyncMock()
        wine_name = "Wine Without Pairings"
        
        mock_wine = MagicMock(spec=WineSummary)
        mock_wine.food_pairing_categories = []
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_wine
        mock_session.execute.return_value = mock_result
        
        wine, categories = await get_wine_and_pairings(mock_session, wine_name)
        
        assert wine == mock_wine
        assert categories == []
        assert mock_session.execute.called


class TestFoodPairingModels:
    
    def test_food_pairing_category_to_dict(self):
        mock_wine_summary = MagicMock()
        mock_wine_summary.wine = "Test Wine"
        
        mock_example1 = MagicMock()
        mock_example1.to_dict.return_value = {"food": "Steak", "reason": "Bold flavors"}
        
        mock_example2 = MagicMock()
        mock_example2.to_dict.return_value = {"food": "Lamb", "reason": "Rich pairing"}
        
        category = FoodPairingCategory()
        category.wine_summary = mock_wine_summary
        category.category = "Red Meat"
        category.base_category = "Beef"
        category.examples = [mock_example1, mock_example2]
        
        result = category.to_dict()
        
        assert result["wine"] == "Test Wine"
        assert result["category"] == "Red Meat"
        assert result["base_category"] == "Beef"
        assert len(result["examples"]) == 2
        assert result["examples"][0]["food"] == "Steak"
        assert result["examples"][1]["food"] == "Lamb"
    
    def test_food_pairing_example_to_dict(self):
        example = FoodPairingExample()
        example.food = "Grilled Salmon"
        example.reason = "Light and fresh pairing with crisp white wine"
        
        result = example.to_dict()
        
        assert result["food"] == "Grilled Salmon"
        assert result["reason"] == "Light and fresh pairing with crisp white wine"