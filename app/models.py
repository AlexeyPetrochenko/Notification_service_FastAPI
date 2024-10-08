from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
import enum
import datetime

from app.db import BaseOrm


class StatusCampaign(enum.StrEnum):
    CREATED = 'created'
    RUNNING = 'running'
    FAILED = 'failed'
    DONE = 'done'


class CampaignOrm(BaseOrm):
    __tablename__ = 'campaign'
    
    campaign_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    content: Mapped[str]
    status: Mapped[StatusCampaign]
    launch_date: Mapped[datetime.datetime]
    
    date_created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    date_updated: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=datetime.datetime.now
    )
