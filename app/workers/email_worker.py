import asyncio
import json

from aio_pika.abc import AbstractIncomingMessage
from httpx import AsyncClient

from app.schemas import NotificationBody, StatusNotification
from app.clients.broker_client import RabbitMQClient
from app.clients.email_client import EmailClient
from app.clients.api_client import ApiClient
from app.exceptions import EmailSendException
from app.config import load_from_env
from app.server import get_logger


# TODO ALexP: Передать logger в класс
logger = get_logger()


class EmailWorker:
    def __init__(self, broker_client: RabbitMQClient, email_client: EmailClient, api_client: ApiClient) -> None:
        self.broker_client = broker_client
        self.email_client = email_client
        self.api_client = api_client
        
    async def consume_message(self) -> None:
        await self.broker_client.connect()
        channel = self.broker_client.channel
        queue = await channel.declare_queue("email_queue", durable=True)
        await queue.consume(callback=self.process_sending_message)
        await asyncio.Future()

    async def process_sending_message(self, message: AbstractIncomingMessage) -> None:
        async with message.process():          
            logger.info("Сообщение взято в работу")
            
            body = NotificationBody(**json.loads(message.body.decode()))
            logger.info("Сообщение обработано")
            
            msg = self.email_client.make_message(body)
            logger.info("Сообщение подготовлено email_client")
            
            try:
                self.email_client.send_notification(body, msg)
                logger.info("Успешно отправлено сообщение")
                await self.api_client.update_notification_status(
                    body.recipient_id, body.campaign_id, StatusNotification.DELIVERED
                )
                logger.info("Статус сообщения в БД изменен на DELIVERED")
            except EmailSendException:
                await self.api_client.update_notification_status(
                    body.
                    recipient_id, body.campaign_id, StatusNotification.UNDELIVERED
                )
                logger.info("Статус сообщения в БД изменен на UNDELIVERED")
                
                
if __name__ == '__main__':
    config = load_from_env()
    api_client = ApiClient(AsyncClient(base_url=config.APP_URL, headers={'Authorization': config.TOKEN_WORKER}))
    email_worker = EmailWorker(RabbitMQClient(config), EmailClient(config), api_client)
    asyncio.run(email_worker.consume_message())
