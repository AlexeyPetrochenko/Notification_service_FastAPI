from pydantic import BaseModel, ConfigDict
from .models import StatusCampaign
import datetime
    
    
# TODO @AlexP: Оставляем только ее
class CampaignSC(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    campaign_id: int
    name: str
    content: str
    status: StatusCampaign
    launch_date: datetime.datetime

    date_created: datetime.datetime
    date_updated: datetime.datetime
