import asyncio
from sqlalchemy import select, and_
from datetime import datetime
from typing import Sequence, Coroutine
import httpx
from dataclasses import dataclass

from app.db import AsyncSessionLocal
from app.models import CampaignOrm, StatusCampaign, StatusNotification
from app.config import settings 
    
    
async def fetch_campaigns_to_launched() -> Sequence[CampaignOrm]:
    async with AsyncSessionLocal() as session:
        query = select(CampaignOrm).where(
            and_(
                CampaignOrm.launch_date <= datetime.now(),
                CampaignOrm.status == StatusCampaign.CREATED
            )
        )
        result = await session.execute(query)
        campaigns = result.scalars().all()
        return campaigns


async def fetch_recipients() -> list | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f'{settings.APP_HOST}/recipients/')
        response.raise_for_status()
        return response.json()
      
      
async def create_notification(campaign_id: int, recipient_id: int) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url=f'{settings.APP_HOST}/notifications/',
            json={
                'status': StatusNotification.PENDING,
                'campaign_id': campaign_id,
                'recipient_id': recipient_id
            }
        )
        response.raise_for_status() 
        return response.json()


async def prepare_notifications(campaign: CampaignOrm) -> list:
    recipients = await fetch_recipients()
    campaign_id = campaign.campaign_id
    tasks: list[Coroutine] = []
    if recipients:
        for recipient in recipients:
            recipient_id = recipient['recipient_id']
            tasks.append(create_notification(campaign_id, recipient_id))
    return tasks


async def campaign_worker() -> None:
    while True:
        campaigns = await fetch_campaigns_to_launched()
        for campaign in campaigns:
            campaign_id = campaign.campaign_id
            tasks_notifications = await prepare_notifications(campaign)
            notifications = await asyncio.gather(*tasks_notifications)
            print(notifications)
            async with httpx.AsyncClient() as client:
                await client.post(f'{settings.APP_HOST}/campaigns/{campaign_id}/run', json={})
        print('CIRCLE')      
        await asyncio.sleep(5)


# TODO: Можно сделать запуск воркера вместе с приложение через lifespan
if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    loop.create_task(campaign_worker())
    loop.run_forever()
