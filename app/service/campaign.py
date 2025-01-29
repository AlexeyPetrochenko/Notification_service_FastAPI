from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter

from app.repository.campaign import CampaignRepository
from app.repository.notification import NotificationRepository
from app.models import StatusCampaign, StatusNotification
from app.exceptions import ConflictException, NotFoundException


class CampaignService:  
    def __init__(
        self, campaign_repository: CampaignRepository, notification_repository: NotificationRepository
    ) -> None:
        self.campaign_repository = campaign_repository
        self.notification_repository = notification_repository
    
    async def complete(
        self, 
        campaign_id: int, 
        session: AsyncSession, 
    ) -> None:
        campaign = await self.campaign_repository.get(campaign_id, session)
        if campaign.status != StatusCampaign.RUNNING:
            raise ConflictException(f'Campaigns with [status: {campaign.status}] cannot be completion')
        
        notifications = await self.notification_repository.get_notifications_by_campaign_id(campaign_id, session)
        if notifications == []:
            raise NotFoundException(f'There are no notifications in this campaign [id: {campaign_id}].')
        
        notifications_statistic = Counter([notification.status for notification in notifications])
        percentage_delivered = (
            notifications_statistic[StatusNotification.DELIVERED] / notifications_statistic.total() * 100
        )

        if percentage_delivered > 80:
            await self.campaign_repository.complete(session, campaign_id, StatusCampaign.DONE)
        else:
            await self.campaign_repository.complete(session, campaign_id, StatusCampaign.FAILED)    
