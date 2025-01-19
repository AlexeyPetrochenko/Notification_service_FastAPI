from app.repository.campaign import CampaignRepository
from app.repository.notification import NotificationRepository
from app.service import CampaignService


def get_campaign_repository() -> CampaignRepository:
    return CampaignRepository()


def get_notification_repository() -> NotificationRepository:
    return NotificationRepository()


def get_service() -> CampaignService:
    return CampaignService()
