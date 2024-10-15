from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, ForeignKey
import enum
import datetime

from app.db import BaseOrm


class StatusCampaign(enum.StrEnum):
    CREATED = 'created'
    RUNNING = 'running'
    FAILED = 'failed'
    DONE = 'done'
    
    
class StatusNotification(enum.StrEnum):
    PENDING = 'pending'
    SENT = 'sent'
    DELIVERED = 'delivered'
    UNDELIVERED = 'undelivered'


class CampaignOrm(BaseOrm):
    __tablename__ = 'campaigns'
    
    campaign_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    content: Mapped[str]
    status: Mapped[StatusCampaign]
    launch_date: Mapped[datetime.datetime]
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=datetime.datetime.now
    )
    notifications: Mapped[list['NotificationOrm']] = relationship()
    

class RecipientOrm(BaseOrm):
    __tablename__ = 'recipients'
    
    recipient_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    lastname: Mapped[str]
    age: Mapped[int]
    contact_email: Mapped[str] = mapped_column(unique=True)

    notifications: Mapped[list['NotificationOrm']] = relationship()
    

class NotificationOrm(BaseOrm):
    __tablename__ = 'notifications'
    
    notification_id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[StatusNotification]
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.campaign_id', ondelete='CASCADE'))
    recipient_id: Mapped[int] = mapped_column(ForeignKey('recipients.recipient_id', ondelete='CASCADE'))

    campaign: Mapped['CampaignOrm'] = relationship()
    recipient: Mapped['RecipientOrm'] = relationship()
