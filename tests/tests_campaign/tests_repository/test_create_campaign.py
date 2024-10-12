import pytest
from fastapi import HTTPException
from sqlalchemy import select
from datetime import datetime

from app.models import CampaignOrm


async def test__create_campaign__campaign_created_success(
    prepare_database, 
    campaign_repository, 
    test_session, 
    campaign_data_factory,
    make_campaign
): 
    data = campaign_data_factory()

    new_campaign = await campaign_repository.create_campaign(**data)     
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    campaign = result.scalars().first()
    
    assert campaign is not None    
    assert isinstance(campaign, CampaignOrm)


async def test__create_campaign__all_fields_created(prepare_database, campaign_repository, campaign_data_factory):
    data = campaign_data_factory()
    
    new_campaign = await campaign_repository.create_campaign(**data)
    
    assert new_campaign.name == data['name']
    assert new_campaign.content == data['content']
    assert new_campaign.status == data['status']
    assert new_campaign.launch_date == data['launch_date']
    

async def test__create_campaign__exception_when_adding_campaign_with_taken_name(
    prepare_database, 
    campaign_repository, 
    campaign_data_factory
):
    data = campaign_data_factory(name='Taken name')
    await campaign_repository.create_campaign(**data)
    
    with pytest.raises(HTTPException):
        await campaign_repository.create_campaign(**data)
        

async def test__create_campaign__campaign_has_creation_and_update_dates(
    prepare_database, 
    campaign_repository, 
    campaign_data_factory
):
    campaign = await campaign_repository.create_campaign(**campaign_data_factory())
    
    assert isinstance(campaign.created_at, datetime) and isinstance(campaign.updated_at, datetime)
     
