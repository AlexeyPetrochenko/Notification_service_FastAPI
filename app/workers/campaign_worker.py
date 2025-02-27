import asyncio
import logging
import logging.config

import aio_pika
from httpx import AsyncClient

from app.config import load_from_env
from app.schemas import Recipient, NotificationBody, Campaign
from app.exceptions import ApiClientException
from app.clients.broker_client import RabbitMQClient
from app.clients.api_client import ApiClient


logger = logging.getLogger('app.workers.campaign_worker')

            
class CampaignWorker: 
    def __init__(self, api_client: ApiClient, broker_client: RabbitMQClient) -> None:
        self. api_client = api_client
        self.broker_client = broker_client
         
    def make_message(self, recipient: Recipient, campaign: Campaign) -> aio_pika.Message:
        body_message = NotificationBody(
            recipient_id=recipient.recipient_id,
            email=recipient.contact_email,
            first_name=recipient.name,
            last_name=recipient.lastname,
            campaign_id=campaign.campaign_id,
            campaign_title=campaign.name,
            content=campaign.content
        )
        
        return aio_pika.Message(
            body=body_message.model_dump_json().encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,  
            headers={
                "message_type": "notification",
                "encoding": "utf-8"
            }
        )
        
    async def add_to_queue(self, message: aio_pika.Message) -> None:
        await self.broker_client.connect()
        channel = self.broker_client.channel
        queue: aio_pika.abc.AbstractQueue = await channel.declare_queue("email_queue", durable=True)     
        await channel.default_exchange.publish(message, routing_key=queue.name)
        
    async def run_campaign(self) -> Campaign:
        campaign = await self.api_client.acquire_campaign_for_launch()
        recipients = await self.api_client.fetch_recipients()
        await self.api_client.prepare_notifications(campaign, recipients)
        for recipient in recipients:
            message = self.make_message(recipient, campaign)
            try:
                await self.add_to_queue(message)
            except Exception:
                logger.exception(
                    'Failed to add message to queue, campaign_id: %(campaign_id)s, recipient_id: %(recipient_id)s',
                    {
                        'campaign_id': campaign.campaign_id,
                        'recipient_id': recipient.recipient_id
                    }
                )
        return campaign
    
    async def complete_campaign(self) -> Campaign:
        campaign = await self.api_client.complete_campaign()
        return campaign
        
    async def main(self) -> None:
        logger.info('CampaignWorker has started successfully')
        while True:
            try:  
                campaign = await self.run_campaign()
                logger.info('The campaign_id: %s has started successfully', campaign.campaign_id)
            except ApiClientException:
                logger.info('There are no campaigns to run')
            try:
                campaign = await self.complete_campaign()
                logger.info('The campaign_id: %s has been successfully completed', campaign.campaign_id)
                
            except ApiClientException:
                logger.info('There are no campaigns to complete.')
            await asyncio.sleep(10)
            
            
if __name__ == '__main__':
    config = load_from_env()
    app_client = AsyncClient(base_url=config.APP_URL, headers={'Authorization': config.TOKEN_WORKER})
    worker = CampaignWorker(ApiClient(app_client), RabbitMQClient(config))
    asyncio.run(worker.main())

        
