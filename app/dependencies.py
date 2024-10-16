from fastapi import HTTPException

from app.db import AsyncSessionLocal
from app.models import CampaignOrm, RecipientOrm
from app.schemas import NotificationCreate


async def presence_in_database(notification_data: NotificationCreate) -> NotificationCreate:
    async with AsyncSessionLocal() as session:
        campaign = await session.get(CampaignOrm, notification_data.campaign_id)
        recipient = await session.get(RecipientOrm, notification_data.recipient_id)
        if campaign is None:
            raise HTTPException(
                status_code=404,
                detail=f'Key (campaign_id)=({notification_data.campaign_id}) is not present in table "campaigns".'
            )
        if recipient is None:
            raise HTTPException(
                status_code=404,
                detail=f'Key (recipient_id)=({notification_data.recipient_id}) is not present in table "recipient".'
            )
        return notification_data
