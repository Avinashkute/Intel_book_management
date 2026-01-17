from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.models.models import Review
from app.schemas.schemas import ReviewCreate
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReviewService:
    async def create_review(self, db: AsyncSession, book_id: int, user_id: int, review_data: ReviewCreate) -> Review:
        try:
            review = Review(
                book_id=book_id,
                user_id=user_id,
                review_text=review_data.review_text,
                rating=review_data.rating
            )
            db.add(review)
            await db.commit()
            await db.refresh(review)
            logger.info(f"Review created for book {book_id} by user {user_id}")
            return review
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating review: {str(e)}")
            raise

    async def get_reviews_by_book(self, db: AsyncSession, book_id: int) -> List[Review]:
        result = await db.execute(select(Review).where(Review.book_id == book_id))
        return result.scalars().all()

    async def get_average_rating(self, db: AsyncSession, book_id: int) -> float:
        result = await db.execute(
            select(func.avg(Review.rating)).where(Review.book_id == book_id)
        )
        avg = result.scalar()
        return round(float(avg), 2) if avg else 0.0

    async def get_review_count(self, db: AsyncSession, book_id: int) -> int:
        result = await db.execute(
            select(func.count(Review.id)).where(Review.book_id == book_id)
        )
        return result.scalar() or 0
