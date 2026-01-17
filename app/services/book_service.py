from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.models.models import Book
from app.schemas.schemas import BookCreate, BookUpdate
from app.services.ai_service import AIService
from app.core.logging import get_logger

logger = get_logger(__name__)


class BookService:
    def __init__(self):
        self.ai_service = AIService()

    async def create_book(self, db: AsyncSession, book_data: BookCreate) -> Book:
        try:
            summary = await self.ai_service.generate_book_summary(
                book_data.title, book_data.author, book_data.genre, book_data.year_published
            )
            book = Book(**book_data.model_dump(), summary=summary)
            db.add(book)
            await db.commit()
            await db.refresh(book)
            logger.info(f"Book created: {book.title}")
            return book
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating book: {str(e)}")
            raise

    async def get_books(self, db: AsyncSession) -> List[Book]:
        result = await db.execute(select(Book))
        return result.scalars().all()

    async def get_book_by_id(self, db: AsyncSession, book_id: int) -> Optional[Book]:
        result = await db.execute(select(Book).where(Book.id == book_id))
        return result.scalar_one_or_none()

    async def update_book(self, db: AsyncSession, book_id: int, book_data: BookUpdate) -> Optional[Book]:
        try:
            book = await self.get_book_by_id(db, book_id)
            if not book:
                return None
            
            update_data = book_data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(book, key, value)
            
            await db.commit()
            await db.refresh(book)
            logger.info(f"Book updated: {book.title}")
            return book
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating book: {str(e)}")
            raise

    async def delete_book(self, db: AsyncSession, book_id: int) -> bool:
        try:
            book = await self.get_book_by_id(db, book_id)
            if not book:
                return False
            await db.delete(book)
            await db.commit()
            logger.info(f"Book deleted: {book_id}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting book: {str(e)}")
            raise

    async def get_books_by_genre(self, db: AsyncSession, genre: str, limit: int = 5) -> List[Book]:
        result = await db.execute(select(Book).where(Book.genre == genre).limit(limit))
        return result.scalars().all()
