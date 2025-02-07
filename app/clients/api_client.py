from httpx import AsyncClient

from app.exceptions import ApiClientException
from app.schemas import Notification, Campaign, Recipient, StatusNotification


class ApiClient:
    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        
    async def prepare_notifications(self, campaign: Campaign, recipients: list[Recipient]) -> list[Notification]:
        recipients_id = [recipient.recipient_id for recipient in recipients]
        response = await self.client.post(
            '/notifications/add/many', 
            json={'campaign_id': campaign.campaign_id, 'recipients_id': recipients_id}
        )
        if response.status_code != 201:
            raise ApiClientException(status_code=422, detail='Failed to receive notifications')
        return [Notification(**notification) for notification in response.json()]
        
    async def fetch_recipients(self) -> list[Recipient]:
        response = await self.client.get('/recipients/')
        if response.status_code != 200: 
            raise ApiClientException(status_code=422, detail='Failed to get recipients')
        return [Recipient(**recipient) for recipient in response.json()]
    
    async def acquire_campaign_for_launch(self) -> Campaign:
        response = await self.client.post('/campaigns/acquire')
        if response.status_code != 200:
            raise ApiClientException(status_code=422, detail='No available campaigns for launch')
        return Campaign(**response.json())
    
    async def update_notification_status(
        self, recipient_id: int, campaign_id: int, status_notification: StatusNotification
    ) -> None:
        response = await self.client.post(
            f'/notifications/{campaign_id}/recipients/{recipient_id}/run',
            json={'status': status_notification}
        )
        if response.status_code != 200:
            raise ApiClientException(status_code=404, detail='Failed receiving notification for update')
        
    async def complete_campaign(self) -> Campaign:
        response = await self.client.post('/campaigns/complete/')
        if response.status_code != 200:
            raise ApiClientException(status_code=422, detail='Failed to complete campaign')
        return Campaign(**response.json())
