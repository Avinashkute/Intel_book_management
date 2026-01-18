import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import Base, get_db
from app.core.config import get_settings
from app.models.models import User, Book, Review, UserRole
from app.core.security import get_password_hash

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

settings = get_settings()

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def async_session(async_engine):
    """Create test database session."""
    async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
async def override_get_db(async_session):
    """Override database dependency."""
    async def _override_get_db():
        yield async_session
    return _override_get_db

@pytest.fixture
async def client(override_get_db):
    """Create test client."""
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(async_session):
    """Create test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        role=UserRole.USER,
        preferred_genre="fiction"
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user

@pytest.fixture
async def test_admin(async_session):
    """Create test admin user."""
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass123"),
        role=UserRole.ADMIN,
        preferred_genre="non-fiction"
    )
    async_session.add(admin)
    await async_session.commit()
    await async_session.refresh(admin)
    return admin

@pytest.fixture
async def test_book(async_session):
    """Create test book."""
    book = Book(
        title="Test Book",
        author="Test Author",
        genre="fiction",
        year_published="2023",
        summary="A test book summary"
    )
    async_session.add(book)
    await async_session.commit()
    await async_session.refresh(book)
    return book

@pytest.fixture
async def user_token(client, test_user):
    """Get user authentication token."""
    response = await client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    return response.json()["access_token"]

@pytest.fixture
async def admin_token(client, test_admin):
    """Get admin authentication token."""
    response = await client.post("/auth/login", json={
        "email": "admin@example.com",
        "password": "adminpass123"
    })
    return response.json()["access_token"]