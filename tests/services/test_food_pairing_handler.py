import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError
from app.services.handlers.food_pairing_handler import (
    handle_cached_pairings,
    handle_food_pairing
)
from app.db.models.wine_summary import WineSummary
from app.db.models.food_pairing import FoodPairingCategory, FoodPairingExample
from app.models.mcp_model import FoodPairingMCPOutput


class TestFoodPairingHandler:
    
    @pytest.mark.asyncio
    async def test_handle_cached_pairings_with_existing_data(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock()
        mock_wine.food_pairing_categories = [MagicMock()]
        
        mock_category = MagicMock()
        mock_category.to_dict.return_value = {
            "category": "Beef",
            "base_category": "Beef",
            "examples": [{"food": "Steak", "reason": "Bold flavors"}]
        }
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_and_pairings') as mock_get:
            mock_get.return_value = (mock_wine, [mock_category])
            
            result, wine = await handle_cached_pairings(mock_session, wine_name)
            
            assert result is not None
            assert result["status"] == "cached"
            assert result["input"]["wine_name"] == wine_name
            assert isinstance(result["output"], FoodPairingMCPOutput)
            assert wine == mock_wine
    
    @pytest.mark.asyncio
    async def test_handle_cached_pairings_no_pairings(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock()
        mock_wine.food_pairing_categories = []
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_and_pairings') as mock_get:
            mock_get.return_value = (mock_wine, [])
            
            result, wine = await handle_cached_pairings(mock_session, wine_name)
            
            assert result is None
            assert wine == mock_wine
    
    @pytest.mark.asyncio
    async def test_handle_cached_pairings_no_wine(self):
        mock_session = AsyncMock()
        wine_name = "Nonexistent Wine"
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_and_pairings') as mock_get:
            mock_get.return_value = (None, [])
            
            result, wine = await handle_cached_pairings(mock_session, wine_name)
            
            assert result is None
            assert wine is None
    
    @pytest.mark.asyncio
    async def test_handle_food_pairing_wine_not_found(self):
        mock_session = AsyncMock()
        wine_name = "Nonexistent Wine"
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_summary_by_name') as mock_get:
            mock_get.return_value = None
            
            result = await handle_food_pairing(mock_session, wine_name)
            
            assert result["status"] == "error"
            assert "not found" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_food_pairing_success(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock()
        mock_wine.id = 1
        mock_wine.to_dict.return_value = {"wine": wine_name, "region": "Test Region"}
        
        mock_gemini_response = '''[
            {
                "category": "Beef",
                "examples": [
                    {"food": "Grilled Steak", "reason": "Bold tannins complement rich meat"}
                ]
            }
        ]'''
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_summary_by_name') as mock_get_wine, \
             patch('app.services.handlers.food_pairing_handler.generate_food_pairing_prompt') as mock_prompt, \
             patch('app.services.handlers.food_pairing_handler.call_gemini_sync_with_retry') as mock_gemini, \
             patch('app.services.handlers.food_pairing_handler.parse_json_from_text') as mock_parse, \
             patch('app.services.handlers.food_pairing_handler.find_base_category') as mock_classify, \
             patch('app.services.handlers.food_pairing_handler.save_food_pairings') as mock_save:
            
            mock_get_wine.return_value = mock_wine
            mock_prompt.return_value = "test prompt"
            mock_gemini.return_value = mock_gemini_response
            mock_parse.return_value = [
                {
                    "category": "Beef",
                    "examples": [
                        {"food": "Grilled Steak", "reason": "Bold tannins complement rich meat"}
                    ]
                }
            ]
            mock_classify.return_value = "Beef"
            mock_save.return_value = None
            
            result = await handle_food_pairing(mock_session, wine_name)
            
            assert result["status"] == "paired"
            assert result["input"]["wine_name"] == wine_name
            assert isinstance(result["output"], FoodPairingMCPOutput)
            assert len(result["output"].pairings) == 1
            assert result["output"].pairings[0].category == "Beef"
            assert result["output"].pairings[0].base_category == "Beef"
            
            mock_save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_handle_food_pairing_with_existing_wine(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock()
        mock_wine.id = 1
        mock_wine.to_dict.return_value = {"wine": wine_name, "region": "Test Region"}
        
        mock_gemini_response = '''[
            {
                "category": "Seafood",
                "examples": [
                    {"food": "Grilled Salmon", "reason": "Light and fresh pairing"}
                ]
            }
        ]'''
        
        with patch('app.services.handlers.food_pairing_handler.generate_food_pairing_prompt') as mock_prompt, \
             patch('app.services.handlers.food_pairing_handler.call_gemini_sync_with_retry') as mock_gemini, \
             patch('app.services.handlers.food_pairing_handler.parse_json_from_text') as mock_parse, \
             patch('app.services.handlers.food_pairing_handler.find_base_category') as mock_classify, \
             patch('app.services.handlers.food_pairing_handler.save_food_pairings') as mock_save:
            
            mock_prompt.return_value = "test prompt"
            mock_gemini.return_value = mock_gemini_response
            mock_parse.return_value = [
                {
                    "category": "Seafood",
                    "examples": [
                        {"food": "Grilled Salmon", "reason": "Light and fresh pairing"}
                    ]
                }
            ]
            mock_classify.return_value = "Seafood"
            mock_save.return_value = None
            
            result = await handle_food_pairing(mock_session, wine_name, wine=mock_wine)
            
            assert result["status"] == "paired"
            assert result["output"].pairings[0].category == "Seafood"
            assert result["output"].pairings[0].base_category == "Seafood"
    
    @pytest.mark.asyncio
    async def test_handle_food_pairing_gemini_error(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock()
        mock_wine.to_dict.return_value = {"wine": wine_name, "region": "Test Region"}
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_summary_by_name') as mock_get_wine, \
             patch('app.services.handlers.food_pairing_handler.generate_food_pairing_prompt') as mock_prompt, \
             patch('app.services.handlers.food_pairing_handler.call_gemini_sync_with_retry') as mock_gemini:
            
            mock_get_wine.return_value = mock_wine
            mock_prompt.return_value = "test prompt"
            mock_gemini.side_effect = Exception("Gemini API error")
            
            result = await handle_food_pairing(mock_session, wine_name)
            
            assert result["status"] == "error"
            assert "Failed to generate pairing" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_food_pairing_invalid_json_response(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock()
        mock_wine.to_dict.return_value = {"wine": wine_name, "region": "Test Region"}
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_summary_by_name') as mock_get_wine, \
             patch('app.services.handlers.food_pairing_handler.generate_food_pairing_prompt') as mock_prompt, \
             patch('app.services.handlers.food_pairing_handler.call_gemini_sync_with_retry') as mock_gemini, \
             patch('app.services.handlers.food_pairing_handler.parse_json_from_text') as mock_parse:
            
            mock_get_wine.return_value = mock_wine
            mock_prompt.return_value = "test prompt"
            mock_gemini.return_value = "invalid response"
            mock_parse.return_value = "not a list"
            
            result = await handle_food_pairing(mock_session, wine_name)
            
            assert result["status"] == "error"
            assert "Failed to generate pairing" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_food_pairing_validation_error(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock()
        mock_wine.to_dict.return_value = {"wine": wine_name, "region": "Test Region"}
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_summary_by_name') as mock_get_wine, \
             patch('app.services.handlers.food_pairing_handler.generate_food_pairing_prompt') as mock_prompt, \
             patch('app.services.handlers.food_pairing_handler.call_gemini_sync_with_retry') as mock_gemini, \
             patch('app.services.handlers.food_pairing_handler.parse_json_from_text') as mock_parse, \
             patch('app.services.handlers.food_pairing_handler.find_base_category') as mock_classify:
            
            mock_get_wine.return_value = mock_wine
            mock_prompt.return_value = "test prompt"
            mock_gemini.return_value = "response"
            mock_parse.return_value = [{"invalid": "data"}]
            mock_classify.return_value = "Other"
            
            result = await handle_food_pairing(mock_session, wine_name)
            
            assert result["status"] == "error"
            assert "Invalid format" in result["error"]
    
    @pytest.mark.asyncio
    async def test_handle_food_pairing_database_save_error(self):
        mock_session = AsyncMock()
        wine_name = "Test Wine"
        
        mock_wine = MagicMock()
        mock_wine.id = 1
        mock_wine.to_dict.return_value = {"wine": wine_name, "region": "Test Region"}
        
        mock_gemini_response = '''[
            {
                "category": "Cheese",
                "examples": [
                    {"food": "Aged Cheddar", "reason": "Complements wine acidity"}
                ]
            }
        ]'''
        
        with patch('app.services.handlers.food_pairing_handler.get_wine_summary_by_name') as mock_get_wine, \
             patch('app.services.handlers.food_pairing_handler.generate_food_pairing_prompt') as mock_prompt, \
             patch('app.services.handlers.food_pairing_handler.call_gemini_sync_with_retry') as mock_gemini, \
             patch('app.services.handlers.food_pairing_handler.parse_json_from_text') as mock_parse, \
             patch('app.services.handlers.food_pairing_handler.find_base_category') as mock_classify, \
             patch('app.services.handlers.food_pairing_handler.save_food_pairings') as mock_save:
            
            mock_get_wine.return_value = mock_wine
            mock_prompt.return_value = "test prompt"
            mock_gemini.return_value = mock_gemini_response
            mock_parse.return_value = [
                {
                    "category": "Cheese",
                    "examples": [
                        {"food": "Aged Cheddar", "reason": "Complements wine acidity"}
                    ]
                }
            ]
            mock_classify.return_value = "Cheese"
            mock_save.side_effect = Exception("Database error")
            
            result = await handle_food_pairing(mock_session, wine_name)
            
            assert result["status"] == "paired"
            assert result["output"].pairings[0].category == "Cheese"