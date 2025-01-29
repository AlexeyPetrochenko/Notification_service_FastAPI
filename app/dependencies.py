from typing import Annotated

from fastapi import Depends

from app.repository.campaign import CampaignRepository
from app.repository.notification import NotificationRepository
from app.repository.user import UserRepository
from app.service.campaign import CampaignService
from app.service.user import UserService


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
