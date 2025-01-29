from typing import Annotated

from fastapi import APIRouter, status, Body, Depends
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.schemas import User
from app.dependencies import get_user_service
from app.service.user import UserService


router = APIRouter(prefix='/users')


@router.post('/', status_code=status.HTTP_201_CREATED)
async def add(
    email: Annotated[EmailStr, Body()],
    password: Annotated[str, Body()],
    service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> User:
    return await service.register_user(session, email, password)
