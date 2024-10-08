import datetime as dt
from sqlalchemy import select

from app.models import CampaignOrm, StatusCampaign


async def test__create_campaign__campaign_created_success(prepare_database, campaign_repository, test_session): 
    data = {
        'name': "Black Friday", 
        'content': "Discounts up to 50%", 
        'status': StatusCampaign.CREATED, 
        'launch_date': dt.datetime(2024, 11, 1, 12, 0, 0)
    }
    
    new_campaign = await campaign_repository.create_campaign(**data)
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    campaign = result.scalars().first()
        
    assert campaign is not None    
    assert campaign.name == data['name']
    assert campaign.content == data['content']
    assert campaign.status == data['status']
    assert campaign.launch_date == data['launch_date']


async def test__create_campaign__return_value_model_object(prepare_database, campaign_repository):
    data = {
        'name': "Black Friday", 
        'content': "Discounts up to 50%", 
        'status': StatusCampaign.CREATED, 
        'launch_date': dt.datetime(2024, 11, 1, 12, 0, 0)
    }
    
    new_campaign = await campaign_repository.create_campaign(**data)
    
    assert isinstance(new_campaign, CampaignOrm)
    assert new_campaign.name == data['name']
    assert new_campaign.content == data['content']
    assert new_campaign.status == data['status']
    assert new_campaign.launch_date == data['launch_date']