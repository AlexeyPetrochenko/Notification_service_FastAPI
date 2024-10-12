import pytest
from fastapi import HTTPException
from datetime import datetime
from sqlalchemy import select

from app.models import StatusCampaign, CampaignOrm


async def test__update_campaign__fields_changed_successfully(prepare_database, campaign_repository, make_campaign, test_session):
    data = {
        'name': 'Name',
        'content': 'Content',
        'status': StatusCampaign.CREATED,
        'launch_date': datetime(2024, 11, 1, 12, 0, 0)
    }
    new_campaign = await make_campaign(**data)
    
    update_campaign = await campaign_repository.update_campaign(
        campaign_id=new_campaign.campaign_id,
        name='New Name',
        content='New Content',
        status=StatusCampaign.DONE,
        launch_date=datetime(2025, 10, 2, 10, 0, 0)
    )
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    campaign = result.scalars().first()
    
    assert update_campaign.name == campaign.name
    assert update_campaign.content == campaign.content
    assert update_campaign.status == campaign.status
    assert update_campaign.launch_date == campaign.launch_date


async def test__update_campaign__updated_date_changed(prepare_database, campaign_repository, campaign_data_factory, make_campaign):
    new_campaign = await make_campaign(**campaign_data_factory(name='Name'))
    
    updated_campaign = await campaign_repository.update_campaign(
        new_campaign.campaign_id,
        **campaign_data_factory(name='New Name')
    )
    
    assert new_campaign.updated_at < updated_campaign.updated_at
    

async def test__update_campaign__exception_campaign_not_found(
    prepare_database, 
    campaign_repository, 
    campaign_data_factory
):
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(1, **campaign_data_factory())


async def test__update_campaign__exception_campaign_name_already_exists(
    prepare_database, 
    campaign_repository,
    campaign_data_factory
):
    first_campaign = await campaign_repository.create_campaign(**campaign_data_factory(name='First'))
    await campaign_repository.create_campaign(**campaign_data_factory(name='Second'))
    
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(first_campaign.campaign_id, **campaign_data_factory(name='Second'))
