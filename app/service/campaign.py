from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.campaign import CampaignRepository
from app.repository.notification import NotificationRepository
from app.schemas import Campaign
from app.exceptions import NoAvailableCampaignsException


class CampaignService:  
    def __init__(
        self, campaign_repository: CampaignRepository, notification_repository: NotificationRepository
    ) -> None:
        self.campaign_repository = campaign_repository
        self.notification_repository = notification_repository
    
    async def complete(self, session: AsyncSession) -> Campaign:
        campaign = await self.campaign_repository.complete(session)
        if campaign is None:
            raise NoAvailableCampaignsException('There are no campaigns available to complete')
        return Campaign.model_validate(campaign) 
