import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from app.services.embedding.food_classifier import find_base_category, CATEGORY_EMBEDDINGS


class TestFoodClassifier:
    
    @patch('app.services.embedding.food_classifier.model')
    def test_find_base_category_exact_match(self, mock_model):
        # Create 384-dimensional embeddings to match the model
        item_embedding = np.zeros(384)
        item_embedding[0] = 1.0
        mock_model.encode.return_value = item_embedding
        
        beef_embedding = np.zeros(384)
        beef_embedding[0] = 1.0
        pork_embedding = np.zeros(384)
        pork_embedding[1] = 1.0
        
        with patch.dict(CATEGORY_EMBEDDINGS, {
            'Beef': [beef_embedding],
            'Pork': [pork_embedding]
        }):
            result = find_base_category("grilled steak")
            assert result == "Beef"
    
    @patch('app.services.embedding.food_classifier.model')
    def test_find_base_category_below_threshold(self, mock_model):
        # Create low similarity embedding
        item_embedding = np.ones(384) * 0.1
        mock_model.encode.return_value = item_embedding
        
        beef_embedding = np.zeros(384)
        beef_embedding[0] = 1.0
        pork_embedding = np.zeros(384)
        pork_embedding[1] = 1.0
        
        with patch.dict(CATEGORY_EMBEDDINGS, {
            'Beef': [beef_embedding],
            'Pork': [pork_embedding]
        }):
            result = find_base_category("random food", threshold=0.5)
            assert result == "Other"
    
    @patch('app.services.embedding.food_classifier.model')
    def test_find_base_category_multiple_embeddings_per_category(self, mock_model):
        item_embedding = np.zeros(384)
        item_embedding[0] = 0.8
        item_embedding[1] = 0.2
        mock_model.encode.return_value = item_embedding
        
        beef_embedding1 = np.zeros(384)
        beef_embedding1[0] = 1.0
        beef_embedding2 = np.zeros(384)
        beef_embedding2[0] = 0.9
        beef_embedding2[1] = 0.1
        pork_embedding = np.zeros(384)
        pork_embedding[1] = 1.0
        
        with patch.dict(CATEGORY_EMBEDDINGS, {
            'Beef': [beef_embedding1, beef_embedding2],
            'Pork': [pork_embedding]
        }):
            result = find_base_category("beef dish")
            assert result == "Beef"
    
    @patch('app.services.embedding.food_classifier.model')
    def test_find_base_category_custom_threshold(self, mock_model):
        item_embedding = np.zeros(384)
        item_embedding[0] = 0.3
        mock_model.encode.return_value = item_embedding
        
        beef_embedding = np.zeros(384)
        beef_embedding[0] = 1.0
        pork_embedding = np.zeros(384)
        pork_embedding[1] = 1.0
        
        with patch.dict(CATEGORY_EMBEDDINGS, {
            'Beef': [beef_embedding],
            'Pork': [pork_embedding]
        }):
            result = find_base_category("beef dish", threshold=0.2)
            assert result == "Beef"
            
            result = find_base_category("beef dish", threshold=0.4)
            assert result == "Other"
    
    @patch('app.services.embedding.food_classifier.model')
    def test_find_base_category_empty_categories(self, mock_model):
        item_embedding = np.zeros(384)
        item_embedding[0] = 1.0
        mock_model.encode.return_value = item_embedding
        
        with patch.dict(CATEGORY_EMBEDDINGS, {}):
            result = find_base_category("any food")
            assert result == "Other"
    
    @patch('app.services.embedding.food_classifier.model')
    def test_find_base_category_input_formatting(self, mock_model):
        item_embedding = np.zeros(384)
        item_embedding[0] = 1.0
        mock_model.encode.return_value = item_embedding
        
        beef_embedding = np.zeros(384)
        beef_embedding[0] = 1.0
        
        with patch.dict(CATEGORY_EMBEDDINGS, {
            'Beef': [beef_embedding]
        }):
            find_base_category("steak")
            mock_model.encode.assert_called_with("A dish of steak", normalize_embeddings=True)
    
    @patch('app.services.embedding.food_classifier.model')
    def test_find_base_category_highest_score_wins(self, mock_model):
        item_embedding = np.zeros(384)
        item_embedding[0] = 0.6
        item_embedding[1] = 0.8
        mock_model.encode.return_value = item_embedding
        
        beef_embedding = np.zeros(384)
        beef_embedding[0] = 1.0
        pork_embedding = np.zeros(384)
        pork_embedding[1] = 1.0
        fish_embedding = np.zeros(384)
        fish_embedding[2] = 1.0
        
        with patch.dict(CATEGORY_EMBEDDINGS, {
            'Beef': [beef_embedding],
            'Pork': [pork_embedding],
            'Fish': [fish_embedding]
        }):
            result = find_base_category("food item")
            assert result == "Pork"