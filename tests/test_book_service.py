import pytest
from unittest.mock import AsyncMock, patch
from app.services.book_service import BookService
from app.models.models import Book
from app.schemas.schemas import BookCreate, BookUpdate

class TestBookService:
    
    @pytest.fixture
    def book_service(self):
        return BookService()
    
    @pytest.fixture
    def mock_db(self):
        return AsyncMock()
    
    @pytest.fixture
    def sample_book_data(self):
        return BookCreate(
            title="Test Book",
            author="Test Author",
            genre="fiction",
            year_published="2023"
        )
    
    async def test_create_book_success(self, book_service, mock_db, sample_book_data):
        """Test successful book creation."""
        # Mock AI service
        with patch.object(book_service.ai_service, 'generate_book_summary') as mock_ai:
            mock_ai.return_value = "AI generated summary"
            
            # Mock database operations
            mock_db.add.return_value = None
            mock_db.commit.return_value = None
            mock_db.refresh.return_value = None
            
            result = await book_service.create_book(mock_db, sample_book_data)
            
            # Assertions
            assert isinstance(result, Book)
            assert result.title == "Test Book"
            assert result.summary == "AI generated summary"
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
    
    async def test_create_book_ai_failure(self, book_service, mock_db, sample_book_data):
        """Test book creation when AI service fails."""
        # Mock AI service failure
        with patch.object(book_service.ai_service, 'generate_book_summary') as mock_ai:
            mock_ai.side_effect = Exception("AI service error")
            mock_db.rollback.return_value = None
            
            with pytest.raises(Exception):
                await book_service.create_book(mock_db, sample_book_data)
            
            mock_db.rollback.assert_called_once()
    
    
    async def test_get_book_by_id_found(self, book_service, mock_db):
        """Test getting book by ID when book exists."""
        expected_book = Book(
            id=1, title="The Alchemist", author="Paulo Coelho", genre="fiction", year_published="1988"
        )
        
        with patch.object(book_service, 'get_book_by_id', return_value=expected_book):
            result = await book_service.get_book_by_id(mock_db, 1)
            
            assert result is not None
            assert result.id == 1
            assert result.title == "The Alchemist"
    
    async def test_get_book_by_id_not_found(self, book_service, mock_db):
        """Test getting book by ID when book doesn't exist."""
        with patch.object(book_service, 'get_book_by_id', return_value=None):
            result = await book_service.get_book_by_id(mock_db, 999)
            
            assert result is None
    
    async def test_update_book_success(self, book_service, mock_db):
        """Test successful book update."""
        # Mock existing book
        existing_book = Book(
            id=1, title="Old Title", author="Test Author", genre="fiction", year_published="2023"
        )
        
        with patch.object(book_service, 'get_book_by_id') as mock_get:
            mock_get.return_value = existing_book
            mock_db.commit = AsyncMock()
            mock_db.refresh = AsyncMock()
            
            update_data = BookUpdate(title="New Title")
            result = await book_service.update_book(mock_db, 1, update_data)
            
            assert result.title == "New Title"
            assert result.author == "Test Author"  # Unchanged
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
    
    async def test_update_book_not_found(self, book_service, mock_db):
        """Test updating non-existent book."""
        with patch.object(book_service, 'get_book_by_id') as mock_get:
            mock_get.return_value = None
            
            update_data = BookUpdate(title="New Title")
            result = await book_service.update_book(mock_db, 999, update_data)
            
            assert result is None
    
    async def test_delete_book_success(self, book_service, mock_db):
        """Test successful book deletion."""
        existing_book = Book(
            id=1, title="Test Book", author="Test Author", genre="fiction", year_published="2023"
        )
        
        with patch.object(book_service, 'get_book_by_id') as mock_get:
            mock_get.return_value = existing_book
            mock_db.delete = AsyncMock()
            mock_db.commit = AsyncMock()
            
            result = await book_service.delete_book(mock_db, 1)
            
            assert result is True
            mock_db.delete.assert_called_once_with(existing_book)
            mock_db.commit.assert_called_once()
    
    async def test_delete_book_not_found(self, book_service, mock_db):
        """Test deleting non-existent book."""
        with patch.object(book_service, 'get_book_by_id') as mock_get:
            mock_get.return_value = None
            
            result = await book_service.delete_book(mock_db, 999)
            
            assert result is False