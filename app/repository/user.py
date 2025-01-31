from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.models import UserOrm


class UserRepository:
    
    async def add(self, session: AsyncSession, email: EmailStr, hash_password: str) -> UserOrm:
        user = UserOrm(email=email, hash_password=hash_password)
        session.add(user)
        await session.commit()
        return user

    async def get(self, session: AsyncSession, user_id: str) -> UserOrm | None:
        user = await session.get(UserOrm, user_id)
        return user

    async def get_by_email(self, session: AsyncSession, email: EmailStr) -> UserOrm | None:
        query = select(UserOrm).where(UserOrm.email == email)
        result = await session.execute(query)
        return result.scalars().first()
