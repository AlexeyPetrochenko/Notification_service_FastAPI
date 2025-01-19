from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from collections import Counter

from app.dependencies import get_campaign_repository, get_notification_repository
from app.repository.campaign import CampaignRepository
from app.repository.notification import NotificationRepository
from app.models import StatusCampaign, StatusNotification
from app.exceptions import ConflictException, NotFoundException


class CampaignService:
    
    async def complete(
        self, 
        campaign_id: int, 
        session: AsyncSession, 
        campaign_repository: CampaignRepository = Depends(get_campaign_repository),
        notification_repository: NotificationRepository = Depends(get_notification_repository),
    ) -> None:
        campaign = await campaign_repository.get(campaign_id, session)
        if campaign.status != StatusCampaign.RUNNING:
            raise ConflictException(f'Campaigns with [status: {campaign.status}] cannot be completion')
        
        notifications = await notification_repository.get_notifications_by_campaign_id(campaign_id, session)
        if notifications == []:
            raise NotFoundException(f'There are no notifications in this campaign [id: {campaign_id}].')
        
        notifications_statistic = Counter([notification.status for notification in notifications])
        percentage_delivered = (
            notifications_statistic[StatusNotification.DELIVERED] / notifications_statistic.total() * 100
        )

        if percentage_delivered > 80:
            campaign.status = StatusCampaign.DONE
        else:
            campaign.status = StatusCampaign.FAILED
        
        await session.commit()
    
