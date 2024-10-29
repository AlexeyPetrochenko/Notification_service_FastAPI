import asyncio
import logging
import random
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

from app.db import AsyncSessionLocal
from app.config import load_from_env
from app.schemas import Recipient, Campaign, Notification, StatusNotification


logging.basicConfig(filename='notification_sending.log', level=logging.INFO)


class WorkerException(Exception):
    def __init__(self, status_code: int, detail: str | None = None):
        self.status_code = status_code
        self.detail = detail


class NotificationSendingWorker:
    def __init__(self, session_maker: Callable[[], AsyncSession], client: AsyncClient) -> None:
        self.session_maker = session_maker 
        self.client = client
        
    async def get_pending_notifications(self, campaign: Campaign, recipients: list[Recipient]) -> list[Notification]:
        recipients_id = [recipient.recipient_id for recipient in recipients]
        response = await self.client.post(
            '/notifications/add/many', 
            json={
                'campaign_id': campaign.campaign_id,
                'recipients_id': recipients_id
            }
        )
        if response.status_code != 201:
            raise WorkerException(status_code=422, detail='Failed to receive notifications')
        return [Notification(**notification) for notification in response.json()]
        
    async def fetch_recipients(self) -> list[Recipient]:
        response = await self.client.get('/recipients/')
        if response.status_code != 200: 
            raise WorkerException(status_code=422, detail='Failed to get recipients')
        return [Recipient(**recipient) for recipient in response.json()]
    
    #TODO @AlexP: Как лучше, выдать исключение и обработать его выше (в even_loop) или возвращать None
    async def acquire_campaign_for_launch(self) -> Campaign:
        response = await self.client.post('/campaigns/acquire')
        if response.status_code != 200:
            # return None
            raise WorkerException(status_code=422, detail='No campaigns available for launch')
        return Campaign(**response.json())

    async def imitation_email_client(self, recipient: Recipient, content: str) -> StatusNotification:
        status_code = random.choices(population=(250, 550), weights=[0.9, 0.1], k=1)[0]
        if status_code != 250:
            logging.info(f'Почта {recipient.contact_email} недействительна!')
            return StatusNotification.UNDELIVERED
        logging.info(f'{recipient.name} {recipient.lastname}-{content}')
        return StatusNotification.SENT
    
    async def send_notification(self, recipient: Recipient, campaign: Campaign) -> None:
        status_notification = await self.imitation_email_client(recipient, campaign.content)
        await self.client.post(
            f'/notifications/{campaign.campaign_id}/{recipient.recipient_id}/run',
            json={'status': status_notification}
        )
            
    async def run(self) -> None:
        while True:
            await asyncio.sleep(5)
            try:  
                campaign = await self.acquire_campaign_for_launch()
                recipients = await self.fetch_recipients()
                await self.get_pending_notifications(campaign, recipients)
                for recipient in recipients:
                    await self.send_notification(recipient, campaign)
            except WorkerException:
                pass 


# TODO: Можно сделать запуск воркера вместе с приложение через lifespan
if __name__ == '__main__':
    config = load_from_env()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    client = AsyncClient(base_url=config.APP_URL)
    worker = NotificationSendingWorker(AsyncSessionLocal, client)
    loop.create_task(worker.run())
    loop.run_forever()

        
