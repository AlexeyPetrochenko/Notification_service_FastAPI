import asyncio
import json
import logging

from aio_pika.abc import AbstractIncomingMessage
from httpx import AsyncClient

from app.schemas import NotificationBody, StatusNotification
from app.clients.broker_client import RabbitMQClient
from app.clients.email_client import EmailClient
from app.clients.api_client import ApiClient
from app.exceptions import EmailSendException
from app.config import load_from_env


logger = logging.getLogger('app.workers.email_worker')


class EmailWorker:
    def __init__(self, broker_client: RabbitMQClient, email_client: EmailClient, api_client: ApiClient) -> None:
        self.broker_client = broker_client
        self.email_client = email_client
        self.api_client = api_client
        
    async def consume_message(self) -> None:
        logger.info('EmailWorker has started successfully')
        await self.broker_client.connect()
        channel = self.broker_client.channel
        queue = await channel.declare_queue("email_queue", durable=True)
        await queue.consume(callback=self.process_sending_message)
        await asyncio.Future()

    async def process_sending_message(self, message: AbstractIncomingMessage) -> None:
        body = NotificationBody(**json.loads(message.body.decode()))
        msg = self.email_client.make_message(body)
        try:
            self.email_client.send_notification(body, msg)
            await self.api_client.update_notification_status(
                body.recipient_id, body.campaign_id, StatusNotification.DELIVERED
            )
            logger.info(
                "Notification sent successfully for recipient_id=%s, campaign_id=%s",
                body.recipient_id,
                body.campaign_id
            )
            await message.ack()
        except EmailSendException:
            await self.api_client.update_notification_status(
                body.
                recipient_id, body.campaign_id, StatusNotification.UNDELIVERED
            )
            logger.warning(
                "Failed to send notification for recipient_id=%s, campaign_id=%s",
                body.recipient_id,
                body.campaign_id
            )
            await message.ack()
                
                
if __name__ == '__main__':
    config = load_from_env()
    api_client = ApiClient(AsyncClient(base_url=config.APP_URL, headers={'Authorization': config.TOKEN_WORKER}))
    email_worker = EmailWorker(RabbitMQClient(config), EmailClient(config), api_client)
    asyncio.run(email_worker.consume_message())
