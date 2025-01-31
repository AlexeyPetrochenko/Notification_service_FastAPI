from typing import Annotated

from fastapi import APIRouter, status, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.schemas import User, Token
from app.dependencies import get_user_service, get_auth_service, get_current_user
from app.service.user import UserService, AuthService


router = APIRouter(prefix='/users')


@router.post('/register/', status_code=status.HTTP_201_CREATED)
async def register(
    email: Annotated[EmailStr, Body()],
    password: Annotated[str, Body()],
    service: Annotated[UserService, Depends(get_user_service)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: User = Depends(get_current_user)  # noqa: U100
) -> User:
    return await service.register_user(session, email, password)


@router.post('/login/')
async def login_for_access_token(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> Token:
    user = await auth_service.authenticate_user(session, email=form_data.username, password=form_data.password)
    token = auth_service.create_token(user.user_id)
    return token
