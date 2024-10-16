from pydantic import BaseModel, ConfigDict, EmailStr
from app.models import StatusCampaign, StatusNotification
import datetime
    

class Campaign(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    campaign_id: int
    name: str
    content: str
    status: StatusCampaign
    launch_date: datetime.datetime

    created_at: datetime.datetime
    updated_at: datetime.datetime


class Recipient(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    recipient_id: int
    name: str
    lastname: str
    age: int
    contact_email: EmailStr
    

class Notification(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    notification_id: int
    status: StatusNotification
    campaign_id: int
    recipient_id: int


class NotificationCreate(BaseModel):
    status: StatusNotification = StatusNotification.PENDING
    campaign_id: int
    recipient_id: int
