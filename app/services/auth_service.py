from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User, UserRole
from app.schemas.schemas import UserCreate
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, verify_refresh_token
from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class AuthService:
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
        try:
            hashed_password = get_password_hash(user_data.password)
            user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=hashed_password,
                role=user_data.role,
                preferred_genre=user_data.preferred_genre
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"User created: {user.username}")
            return user
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
        try:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if not user or not verify_password(password, user.hashed_password):
                return None
            return user
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise

    @staticmethod
    def create_tokens(user: User) -> dict:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.username, "role": user.role.value}
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict:
        payload = verify_refresh_token(refresh_token)
        if not payload:
            raise Exception("Invalid refresh token")
        
        user = await AuthService.get_user_by_username(db, payload["sub"])
        if not user:
            raise Exception("User not found")
        
        return AuthService.create_tokens(user)

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> User:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()
