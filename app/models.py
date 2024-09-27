from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
import enum
import datetime

from .db import BaseOrm


class StatusCampaign(enum.Enum):
    created = 'created'
    running = 'running'
    stopped = 'stopped'
    done = 'done'


class CampaignOrm(BaseOrm):
    __tablename__ = 'campaign'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[str | None]
    status: Mapped[StatusCampaign]
    newsletter_template: Mapped[str]
    launch_date: Mapped[datetime.datetime]
    
    date_created: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    date_updated: Mapped[datetime.datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=datetime.datetime.now
    )
