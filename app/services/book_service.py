from sqlalchemy.orm import Session
from app.models import Book
from app.schemas import BookCreate

class BookService:
    @staticmethod
    def get_all_books(db: Session):
        return db.query(Book).all()

    @staticmethod
    def get_book(db: Session, book_id: int):
        return db.query(Book).filter(Book.id == book_id).first()

    @staticmethod
    def create_book(db: Session, book: BookCreate):
        db_book = Book(**book.dict())
        db.add(db_book)
        db.commit()
        db.refresh(db_book)
        return db_book

    @staticmethod
    def delete_book(db: Session, book_id: int):
        book = db.query(Book).filter(Book.id == book_id).first()
        if book:
            db.delete(book)
            db.commit()
        return book
