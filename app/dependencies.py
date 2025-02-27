from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.campaign import CampaignRepository
from app.repository.notification import NotificationRepository
from app.repository.user import UserRepository
from app.service.campaign import CampaignService
from app.service.user import UserService, AuthService
from app.db import get_db_session
from app.schemas import User
from app.config import load_from_env


get_oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_campaign_repository() -> CampaignRepository:
    return CampaignRepository()


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()


def get_user_repository() -> UserRepository:
    return UserRepository()


def get_campaign_service(
    campaign_repository: Annotated[CampaignRepository, Depends(get_campaign_repository)],
    notification_repository: Annotated[NotificationRepository, Depends(get_notification_repository)] 
) -> CampaignService:
    return CampaignService(campaign_repository, notification_repository)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    return UserService(user_repository)


def get_auth_service(user_repository: Annotated[UserRepository, Depends(get_user_repository)]) -> AuthService:
    return AuthService(user_repository, config=load_from_env())


async def get_current_user(
    token: Annotated[str, Depends(get_oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> User:
    return await auth_service.get_current_user(session, token)
