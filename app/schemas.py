import datetime
import uuid

from pydantic import BaseModel, ConfigDict, EmailStr
from app.models import StatusCampaign, StatusNotification


class Base(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Campaign(Base):
    campaign_id: int
    name: str
    content: str
    status: StatusCampaign
    launch_date: datetime.datetime

    created_at: datetime.datetime
    updated_at: datetime.datetime


class Recipient(Base):
    recipient_id: int
    name: str
    lastname: str
    age: int
    contact_email: EmailStr
    

class Notification(Base):
    notification_id: int
    status: StatusNotification
    campaign_id: int
    recipient_id: int


class User(Base):
    user_id: uuid.UUID
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class NotificationBody(BaseModel):
    recipient_id: int
    email: EmailStr
    first_name: str
    last_name: str
    campaign_id: int
    campaign_title: str
    content: str
