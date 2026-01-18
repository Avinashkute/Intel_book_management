import pytest
from httpx import AsyncClient

class TestAuthAPI:
    
    async def test_register_user_success(self, client: AsyncClient):
        """Test successful user registration."""
        user_data = {
            "username": "Rohit",
            "email": "rohitkute@gmail.com",
            "password": "admin123",
            "role": "user",
            "preferred_genre": "fiction"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "Rohit"
        assert data["email"] == "rohitkute@gmail.com"
        assert data["role"] == "user"
        assert "password" not in data
    
    async def test_register_duplicate_username(self, client: AsyncClient, test_user):
        """Test registration with duplicate username."""
        user_data = {
            "username": "testuser",  # Same as test_user fixture
            "email": "different@example.com",
            "password": "admin123",
            "role": "user"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    async def test_register_invalid_password(self, client: AsyncClient):
        """Test registration with invalid password."""
        user_data = {
            "username": "Rohit",
            "email": "rohitkute@gmail.com",
            "password": "123",  # Too short
            "role": "user"
        }
        
        response = await client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422
        assert "String should have at least 6 characters" in str(response.json())
    
    async def test_login_success(self, client: AsyncClient, test_user):
        """Test successful login."""
        login_data = {
            "email": "test@example.com",  # Match test_user fixture
            "password": "testpass123"      # Match test_user fixture
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_login_invalid_credentials(self, client: AsyncClient, test_user):
        """Test login with invalid credentials."""
        login_data = {
            "email": "avinashkute55@gmail.com",
            "password": "admin2"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        login_data = {
            "email": "laxmikant@gmail.com",
            "password": "password123"
        }
        
        response = await client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    async def test_refresh_token_success(self, client: AsyncClient, test_user):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpass123"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Test refresh
        refresh_data = {"refresh_token": refresh_token}
        response = await client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_refresh_token_invalid(self, client: AsyncClient):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_token"}
        response = await client.post("/auth/refresh", json=refresh_data)
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]