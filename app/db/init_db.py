import asyncio
from sqlalchemy import create_engine
from app.db.session import Base
from app.models.models import User, Book, Review
from app.core.config import get_settings

settings = get_settings()


async def init_db():
    engine = create_engine(settings.DATABASE_URL_SYNC)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
