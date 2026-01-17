from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.schemas.schemas import BookCreate, BookUpdate, BookResponse, BookSummaryResponse, GenerateSummaryRequest
from app.services.book_service import BookService
from app.services.review_service import ReviewService
from app.services.ai_service import AIService
from app.api.dependencies import get_current_user, get_current_admin
from app.models.models import User
from app.core.logging import get_logger

router = APIRouter(prefix="/books", tags=["Books"])
logger = get_logger(__name__)
book_service = BookService()
review_service = ReviewService()
ai_service = AIService()


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    try:
        book = await book_service.create_book(db, book_data)
        return book
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create book"
        )


@router.get("", response_model=List[BookResponse])
async def get_books(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        books = await book_service.get_books(db)
        return books
    except Exception as e:
        logger.error(f"Error fetching books: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch books"
        )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    book = await book_service.get_book_by_id(db, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    try:
        book = await book_service.update_book(db, book_id, book_data)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update book"
        )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    try:
        deleted = await book_service.delete_book(db, book_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete book"
        )


@router.post("/generate-summary", response_model=dict)
async def generate_summary(
    request: GenerateSummaryRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        summary = await ai_service.generate_book_summary(
            request.title, request.author, request.genre, request.year_published
        )
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get("/{book_id}/summary", response_model=dict)
async def get_book_analytics(
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
        avg_rating = await review_service.get_average_rating(db, book_id)
        total_reviews = await review_service.get_review_count(db, book_id)
        
        # Generate AI sentiment analysis
        review_data = [{"rating": r.rating, "review_text": r.review_text} for r in reviews]
        sentiment_summary = await ai_service.generate_review_summary(review_data)
        
        return {
            "book_id": book_id,
            "book_title": book.title,
            "average_rating": round(avg_rating, 2) if avg_rating else 0,
            "sentiment_analysis": sentiment_summary
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching book analytics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch book analytics"
        )

@router.get("/recommendations/", response_model=List[BookResponse])
async def get_recommendations(
    genre: str = Query(None, description="Genre preference for recommendations"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        preferred_genre = genre or current_user.preferred_genre
        if not preferred_genre:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Genre preference required"
            )
        
        books = await book_service.get_books_by_genre(db, preferred_genre)
        return books
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch recommendations"
        )