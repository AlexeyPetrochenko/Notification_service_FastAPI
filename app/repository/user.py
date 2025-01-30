from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr

from app.models import UserOrm
from app.exceptions import ConflictException


class UserRepository:
    async def add(self, session: AsyncSession, email: EmailStr, hash_password: str) -> UserOrm:
        user = UserOrm(email=email, hash_password=hash_password)
        session.add(user)
        try:
            await session.commit()
        except IntegrityError:
            raise ConflictException(detail=f'User with this email: {email} already exists')
        return user
