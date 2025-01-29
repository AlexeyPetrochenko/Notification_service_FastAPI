from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.repository.user import UserRepository
from app.utils import get_password_hash
from app.schemas import User


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository: UserRepository = user_repository
        
    async def register_user(self, session: AsyncSession, email: EmailStr, password: str) -> User:
        user = await self.user_repository.add(session, email, get_password_hash(password))
        return User.model_validate(user)
