import uuid
import enum
import datetime

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

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
    
    notifications: Mapped[list['NotificationOrm']] = relationship(
        "NotificationOrm",
        back_populates="campaign", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, id={self.campaign_id}, status={self.status}>'


class RecipientOrm(BaseOrm):
    __tablename__ = 'recipients'
    
    recipient_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    lastname: Mapped[str]
    age: Mapped[int]
    contact_email: Mapped[str] = mapped_column(unique=True)

    notifications: Mapped[list['NotificationOrm']] = relationship(
        "NotificationOrm",
        back_populates="recipient",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}, id={self.recipient_id}>'


class NotificationOrm(BaseOrm):
    __tablename__ = 'notifications'
    
    notification_id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[StatusNotification]
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaigns.campaign_id', ondelete='CASCADE'))
    recipient_id: Mapped[int] = mapped_column(ForeignKey('recipients.recipient_id', ondelete='CASCADE'))

    campaign: Mapped['CampaignOrm'] = relationship()
    recipient: Mapped['RecipientOrm'] = relationship()

    def __repr__(self) -> str:
        return f'''
    <{self.__class__.__name__}, id={self.notification_id}, 
    campaign_id={self.campaign_id}, recipient_id={self.recipient_id}>
    '''


class UserOrm(BaseOrm):
    __tablename__ = 'users'
    
    user_id: Mapped[uuid.UUID] = mapped_column(UUID, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    hash_password: Mapped[str] = mapped_column(nullable=False)
