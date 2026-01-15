from pydantic import BaseModel

class BookCreate(BaseModel):
    title: str
    author: str
    isbn: str

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    isbn: str

    class Config:
        from_attributes = True
