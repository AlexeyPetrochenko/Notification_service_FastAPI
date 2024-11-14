import asyncio
import smtplib
import logging
from httpx import AsyncClient
from email.message import EmailMessage

from app.config import load_from_env
from app.schemas import Recipient, Campaign, Notification, StatusNotification
from app.exceptions import WorkerException, EmailSendException
from app.server import get_logger


class EmailClient:
    def __init__(self, host: str, port: str, email: str, password: str) -> None:
        self.host = host
        self.port = port
        self.email = email
        self.password = password
        
    async def get_email_server(self) -> smtplib.SMTP_SSL:
        server = smtplib.SMTP_SSL(host=self.host, port=int(self.port))
        server.login(user=self.email, password=self.password)
        return server
        
    async def make_message(self, campaign: Campaign, recipient: Recipient) -> EmailMessage:
        msg = EmailMessage()
        msg['From'] = self.email
        msg['To'] = recipient.contact_email
        msg['Subject'] = campaign.name
        welcome_message = f'Уважаемый {recipient.lastname} {recipient.name}\n'
        msg.set_content(welcome_message + campaign.content, charset='utf-8')
        return msg
        
    async def send_notification(
        self, server: smtplib.SMTP_SSL, recipient: Recipient, campaign: Campaign, message: EmailMessage
    ) -> StatusNotification:
        try:
            server.send_message(msg=message, from_addr=self.email, to_addrs=recipient.contact_email)
            status = StatusNotification.DELIVERED
        except (smtplib.SMTPException, ValueError):
            status = StatusNotification.UNDELIVERED
            raise EmailSendException(campaign.campaign_id, recipient.contact_email)
        finally:
            return status

        
class ApiClient:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        
    async def get_pending_notifications(self, campaign: Campaign, recipients: list[Recipient]) -> list[Notification]:
        recipients_id = [recipient.recipient_id for recipient in recipients]
        response = await self.client.post(
            '/notifications/add/many', 
            json={'campaign_id': campaign.campaign_id, 'recipients_id': recipients_id}
        )
        if response.status_code != 201:
            raise WorkerException(status_code=422, detail='Failed to receive notifications')
        return [Notification(**notification) for notification in response.json()]
        
    async def fetch_recipients(self) -> list[Recipient]:
        response = await self.client.get('/recipients/')
        if response.status_code != 200: 
            raise WorkerException(status_code=422, detail='Failed to get recipients')
        return [Recipient(**recipient) for recipient in response.json()]
    
    async def acquire_campaign_for_launch(self) -> Campaign:
        response = await self.client.post('/campaigns/acquire')
        if response.status_code != 200:
            raise WorkerException(status_code=422, detail='No campaigns available for launch')
        return Campaign(**response.json())
    
    async def update_notification_status(
        self, recipient: Recipient, campaign: Campaign, status_notification: StatusNotification
    ) -> None:
        response = await self.client.post(
            f'/notifications/{campaign.campaign_id}/recipients/{recipient.recipient_id}/run',
            json={'status': status_notification}
        )
        if response.status_code != 200:
            raise WorkerException(status_code=404, detail='Failed receiving notification for update')
        
    async def complete_campaign(self, campaign: Campaign) -> None:
        response = await self.client.post(f'/campaigns/{campaign.campaign_id}/completion')
        if response.status_code != 204:
            raise WorkerException(status_code=422, detail='Failed to complete campaign')
            

class NotificationSendingWorker: 
    def __init__(self, api_client: ApiClient, email_client: EmailClient, logger: logging.Logger) -> None:
        self. api_client = api_client
        self.email_client = email_client
        self.logger = logger
    
    async def run(self) -> None:
        while True:
            await asyncio.sleep(5)
            try:  
                campaign = await self.api_client.acquire_campaign_for_launch()
                recipients = await self.api_client.fetch_recipients()
                await self.api_client.get_pending_notifications(campaign, recipients)
                email_server = await self.email_client.get_email_server()
        
                for recipient in recipients:
                    msg = await self.email_client.make_message(campaign, recipient)
                    try:
                        status = await self.email_client.send_notification(email_server, recipient, campaign, msg)
                    except EmailSendException as err:
                        self.logger.warning(err.detail)
                    finally:
                        await self.api_client.update_notification_status(recipient, campaign, status)
                        
                email_server.close()
                await self.api_client.complete_campaign(campaign)
            except (WorkerException, EmailSendException) as err:
                self.logger.warning(err.detail)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop=loop)
    
    config = load_from_env()
    app_client = AsyncClient(base_url=config.APP_URL)
    logger = get_logger()
    worker = NotificationSendingWorker(
        ApiClient(app_client),
        EmailClient(config.EMAIL_HOST, config.EMAIL_PORT, config.EMAIL_NAME, config.EMAIL_PASS),
        logger
    )
    loop.create_task(worker.run())
    loop.run_forever()

        
