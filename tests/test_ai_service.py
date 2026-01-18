import pytest
from unittest.mock import AsyncMock, patch
from app.services.ai_service import AIService

class TestAIService:
    
    @pytest.fixture
    def ai_service(self):
        return AIService()
    
    @patch('app.services.ai_service.acompletion')
    async def test_generate_book_summary(self, mock_acompletion, ai_service):
        """Test book summary generation."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "A fascinating tale of adventure and discovery."
        mock_acompletion.return_value = mock_response
        
        # Test
        result = await ai_service.generate_book_summary(
            "Clean Code", "Robert C. Martin", "Programming", "2008"
        )
        
        # Assertions
        assert result == "A fascinating tale of adventure and discovery."
        mock_acompletion.assert_called_once()
        
        # Verify prompt structure
        call_args = mock_acompletion.call_args
        assert "Clean Code" in call_args[1]["messages"][0]["content"]
        assert "Robert C. Martin" in call_args[1]["messages"][0]["content"]
    
    @patch('app.services.ai_service.acompletion')
    async def test_generate_review_summary_empty_reviews(self, mock_acompletion, ai_service):
        """Test review summary with empty reviews."""
        result = await ai_service.generate_review_summary([])
        assert result == "No reviews available."
        mock_acompletion.assert_not_called()
    
    @patch('app.services.ai_service.acompletion')
    async def test_generate_review_summary_with_reviews(self, mock_acompletion, ai_service):
        """Test review summary generation with reviews."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.choices = [AsyncMock()]
        mock_response.choices[0].message.content = "Users generally love this book with positive feedback."
        mock_acompletion.return_value = mock_response
        
        # Test data
        reviews = [
            {"rating": 5.0, "review_text": "Amazing book!"},
            {"rating": 4.0, "review_text": "Really enjoyed it."}
        ]
        
        # Test
        result = await ai_service.generate_review_summary(reviews)
        
        # Assertions
        assert result == "Users generally love this book with positive feedback."
        mock_acompletion.assert_called_once()
        
        # Verify prompt contains review data
        call_args = mock_acompletion.call_args
        prompt = call_args[1]["messages"][0]["content"]
        assert "Amazing book!" in prompt
        assert "Really enjoyed it." in prompt
    
    @patch('app.services.ai_service.acompletion')
    async def test_ai_service_error_handling(self, mock_acompletion, ai_service):
        """Test AI service error handling."""
        # Mock exception
        mock_acompletion.side_effect = Exception("API Error")
        
        # Test
        with pytest.raises(Exception) as exc_info:
            await ai_service.generate_book_summary("Clean Code", "Robert C. Martin", "Programming", "2008")
        
        assert "Failed to generate summary" in str(exc_info.value)