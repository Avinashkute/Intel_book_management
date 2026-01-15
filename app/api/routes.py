from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import BookService
from app.schemas import BookCreate, BookResponse

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Book Management API"}

@router.get("/health")
def health_check():
    return {"status": "ok"}

@router.get("/books", response_model=list[BookResponse])
def get_books(db: Session = Depends(get_db)):
    return BookService.get_all_books(db)

@router.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = BookService.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.post("/books", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return BookService.create_book(db, book)

@router.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = BookService.delete_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}
