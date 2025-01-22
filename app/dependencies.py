from fastapi import Depends
from typing import Annotated

from app.repository.campaign import CampaignRepository
from app.repository.notification import NotificationRepository
from app.service import CampaignService


def get_campaign_repository() -> CampaignRepository:
    return CampaignRepository()


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()


def get_service(
    campaign_repository: Annotated[CampaignRepository, Depends(get_campaign_repository)],
    notification_repository: Annotated[NotificationRepository, Depends(get_notification_repository)] 
) -> CampaignService:
    return CampaignService(campaign_repository, notification_repository)
