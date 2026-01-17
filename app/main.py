from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, books, reviews
from app.core.logging import setup_logging
from app.core.config import get_settings
from sqlalchemy import create_engine
from app.db.session import Base
from app.models.models import User, Book, Review

settings = get_settings()
setup_logging()

app = FastAPI(
    title="Book Management System",
    description="Intelligent book management system with AI-powered summaries and recommendations",
    version="1.0.0"
)

@app.on_event("startup")
def init_db():
    import time
    max_retries = 5
    for i in range(max_retries):
        try:
            engine = create_engine(settings.DATABASE_URL_SYNC)
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully!")
            break
        except Exception as e:
            if i < max_retries - 1:
                print(f"Database not ready, retrying in 2 seconds... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(reviews.router)

