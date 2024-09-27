from pydantic import BaseModel
from .models import StatusCampaign
import datetime


class CampaignAddSh(BaseModel):
    name: str
    description: str | None
    status: StatusCampaign
    newsletter_template: str
    launch_date: datetime.datetime
    
    
class CampaignUpdateSh(BaseModel):
    name: str | None
    description: str | None
    status: StatusCampaign | None
    newsletter_template: str | None
    launch_date: datetime.datetime | None


class CampaignIdSh(BaseModel):
    id: int


class CampaignGetSh(CampaignAddSh):
    id: int
    date_created: datetime.datetime
    date_updated: datetime.datetime

    class Config:
        orm_mode = True
        from_attributes = True
