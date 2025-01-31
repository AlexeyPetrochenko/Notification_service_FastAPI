import uuid
from datetime import datetime, timezone, timedelta

import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from app.repository.user import UserRepository
from app.config import Config, load_from_env
from app.utils import get_password_hash, verify_password
from app.schemas import User, Token
from app.exceptions import CredentialsException, ConflictException


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        
    async def register_user(self, session: AsyncSession, email: EmailStr, password: str) -> User:
        try:
            user = await self.user_repository.add(session, email, get_password_hash(password))
        except IntegrityError:
            raise ConflictException(detail=f'User with this email: {email} already exists')
        return User.model_validate(user)


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository
        self.config: Config = load_from_env()
        
    def create_token(self, user_id: uuid.UUID) -> Token:
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.config.JWT_EXP)
        data = {"sub": str(user_id), "exp": expire}
        encoded_jwt = jwt.encode(payload=data, key=self.config.JWT_SECRET, algorithm=self.config.JWT_ALGORITHM)
        return Token(access_token=encoded_jwt, token_type='bearer')

    async def authenticate_user(self, session: AsyncSession, email: EmailStr, password: str) -> User:
        user = await self.user_repository.get_by_email(session, email)
        if not (user and verify_password(password, user.hash_password)):
            raise CredentialsException(detail='Incorrect username or password')
        return User.model_validate(user)
    
    async def get_current_user(self, session: AsyncSession, token: str) -> User:
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET, algorithms=[self.config.JWT_ALGORITHM])
            user_id = payload['sub']
        except (InvalidTokenError, KeyError):
            raise CredentialsException
        
        user = await self.user_repository.get(session, user_id)
        if not user:
            raise CredentialsException
        return User.model_validate(user)
