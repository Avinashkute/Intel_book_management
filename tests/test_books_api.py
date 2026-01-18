import pytest
from unittest.mock import patch
from httpx import AsyncClient

class TestBooksAPI:
    
    async def test_create_book_success(self, client: AsyncClient, admin_token):
        """Test successful book creation by admin."""
        book_data = {
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "genre": "Fiction",
            "year_published": "1988"
        }
        
        with patch('app.services.ai_service.AIService.generate_book_summary') as mock_ai:
            mock_ai.return_value = "AI generated summary"
            
            response = await client.post(
                "/books",
                json=book_data,
                headers={"Authorization": f"Bearer {admin_token}"}
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "The Alchemist"
        assert data["author"] == "Paulo Coelho"
        assert data["summary"] == "AI generated summary"
    
    async def test_create_book_unauthorized(self, client: AsyncClient, user_token):
        """Test book creation by regular user (should fail)."""
        book_data = {
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "genre": "Fiction",
            "year_published": "1988"
        }
        
        response = await client.post(
            "/books",
            json=book_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_create_book_no_auth(self, client: AsyncClient):
        """Test book creation without authentication."""
        book_data = {
            "title": "The Alchemist",
            "author": "Paulo Coelho",
            "genre": "Fiction",
            "year_published": "1998"
        }
        
        response = await client.post("/books", json=book_data)
        
        assert response.status_code == 401
    
    async def test_get_books_success(self, client: AsyncClient, user_token, test_book):
        """Test getting all books."""
        response = await client.get(
            "/books",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == "Test Book"  # Match test_book fixture
    
    async def test_get_book_by_id_success(self, client: AsyncClient, user_token, test_book):
        """Test getting book by ID."""
        response = await client.get(
            f"/books/{test_book.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_book.id
        assert data["title"] == "Test Book"  # Match test_book fixture
    
    async def test_get_book_not_found(self, client: AsyncClient, user_token):
        """Test getting non-existent book."""
        response = await client.get(
            "/books/999",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 404
        assert "Book not found" in response.json()["detail"]
    
    async def test_update_book_success(self, client: AsyncClient, admin_token, test_book):
        """Test successful book update by admin."""
        update_data = {
            "title": "Updated Book Title",
            "summary": "Updated summary"
        }
        
        response = await client.put(
            f"/books/{test_book.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Book Title"
        assert data["summary"] == "Updated summary"
    
    async def test_update_book_unauthorized(self, client: AsyncClient, user_token, test_book):
        """Test book update by regular user (should fail)."""
        update_data = {"title": "Updated Title"}
        
        response = await client.put(
            f"/books/{test_book.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_delete_book_success(self, client: AsyncClient, admin_token, test_book):
        """Test successful book deletion by admin."""
        response = await client.delete(
            f"/books/{test_book.id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 204
    
    async def test_delete_book_unauthorized(self, client: AsyncClient, user_token, test_book):
        """Test book deletion by regular user (should fail)."""
        response = await client.delete(
            f"/books/{test_book.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_generate_summary_success(self, client: AsyncClient, user_token):
        """Test AI summary generation."""
        request_data = {
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "genre": "Programming",
            "year_published": "2008"
        }
        
        with patch('app.services.ai_service.AIService.generate_book_summary') as mock_ai:
            mock_ai.return_value = "Generated summary"
            
            response = await client.post(
                "/books/generate-summary",
                json=request_data,
                headers={"Authorization": f"Bearer {user_token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["summary"] == "Generated summary"
    
    async def test_get_book_analytics_success(self, client: AsyncClient, user_token, test_book):
        """Test book analytics endpoint."""
        with patch('app.services.ai_service.AIService.generate_review_summary') as mock_ai:
            mock_ai.return_value = "Sentiment analysis result"
            
            response = await client.get(
                f"/books/{test_book.id}/summary",
                headers={"Authorization": f"Bearer {user_token}"}
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["book_id"] == test_book.id
        assert data["book_title"] == "Test Book"  # Match test_book fixture
        assert "sentiment_analysis" in data
    
    async def test_get_recommendations_success(self, client: AsyncClient, user_token, test_book):
        """Test book recommendations."""
        response = await client.get(
            "/books/recommendations/?genre=fiction",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)