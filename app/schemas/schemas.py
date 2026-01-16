from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: UserRole = UserRole.USER
    preferred_genre: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    preferred_genre: Optional[str]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    genre: str = Field(..., min_length=1, max_length=50)
    year_published: int = Field(..., ge=1000, le=9999)


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    genre: Optional[str] = Field(None, min_length=1, max_length=50)
    year_published: Optional[int] = Field(None, ge=1000, le=9999)
    summary: Optional[str] = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: str
    year_published: int
    summary: Optional[str]

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    review_text: str = Field(..., min_length=1)
    rating: float = Field(..., ge=0.0, le=5.0)


class ReviewResponse(BaseModel):
    id: int
    book_id: int
    user_id: int
    review_text: str
    rating: float

    class Config:
        from_attributes = True


class BookSummaryResponse(BaseModel):
    book: BookResponse
    average_rating: float
    total_reviews: int
    reviews: List[ReviewResponse]


class GenerateSummaryRequest(BaseModel):
    title: str
    author: str
    genre: str
    year_published: int
