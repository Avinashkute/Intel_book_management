from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.schemas.schemas import ReviewCreate, ReviewResponse
from app.services.review_service import ReviewService
from app.services.book_service import BookService
from app.api.dependencies import get_current_user
from app.models.models import User
from app.core.logging import get_logger

router = APIRouter(prefix="/books", tags=["Reviews"])
logger = get_logger(__name__)
review_service = ReviewService()
book_service = BookService()


@router.post("/{book_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    book_id: int,
    review_data: ReviewCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        book = await book_service.get_book_by_id(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        review = await review_service.create_review(db, book_id, current_user.id, review_data)
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )


@router.get("/{book_id}/reviews", response_model=List[ReviewResponse])
async def get_reviews(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        book = await book_service.get_book_by_id(db, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        
        reviews = await review_service.get_reviews_by_book(db, book_id)
        return reviews
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch reviews"
        )
