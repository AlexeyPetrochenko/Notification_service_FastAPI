from pydantic import BaseModel, ConfigDict
from .models import StatusCampaign
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
