import pytest
from fastapi import HTTPException
from sqlalchemy import select
from datetime import datetime

from app.models import CampaignOrm, StatusCampaign


async def test__create_campaign__campaign_created_success(
    prepare_database,  # noqa: U100
    campaign_repository, 
    test_session, 
    campaign_data_factory,
): 
    data = campaign_data_factory()

    new_campaign = await campaign_repository.create_campaign(**data)     
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    campaign = result.scalars().first()
    
    assert campaign is not None    
    assert isinstance(campaign, CampaignOrm)


async def test__create_campaign__all_fields_created(prepare_database, campaign_repository, campaign_data_factory):   # noqa: U100
    data = campaign_data_factory()
    
    new_campaign = await campaign_repository.create_campaign(**data)
    
    assert new_campaign.name == data['name']
    assert new_campaign.content == data['content']
    assert new_campaign.status == data['status']
    assert new_campaign.launch_date == data['launch_date']
    

async def test__create_campaign__exception_when_adding_campaign_with_taken_name(
    prepare_database,  # noqa: U100
    campaign_repository, 
    campaign_data_factory
):
    data = campaign_data_factory(name='Taken name')
    await campaign_repository.create_campaign(**data)
    
    with pytest.raises(HTTPException):
        await campaign_repository.create_campaign(**data)
        

async def test__create_campaign__campaign_has_creation_and_update_dates(
    prepare_database,  # noqa: U100
    campaign_repository, 
    campaign_data_factory
):
    campaign = await campaign_repository.create_campaign(**campaign_data_factory())
    
    assert isinstance(campaign.created_at, datetime) and isinstance(campaign.updated_at, datetime)


async def test__delete_campaign__success_delete(
    prepare_database,  # noqa: U100 
    campaign_repository, 
    campaign_data_factory, 
    test_session,
    make_campaign
):
    new_campaign = await make_campaign(**campaign_data_factory())
    
    await campaign_repository.delete_campaign(new_campaign.campaign_id)
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    delete_campaign = result.scalars().first()
    
    assert delete_campaign is None


async def test__delete_campaign__exception_campaign_not_found(prepare_database, campaign_repository):  # noqa: U100
    with pytest.raises(HTTPException):
        await campaign_repository.delete_campaign(1)


async def test__get_all_campaigns__check_count_returning_campaigns(
    prepare_database,  # noqa: U100
    campaign_repository,
    campaign_data_factory,
    make_campaign
):
    await make_campaign(**campaign_data_factory(name='First Campaign'))
    await make_campaign(**campaign_data_factory(name='Second Campaign'))
    
    campaigns = await campaign_repository.get_all_campaigns()
    
    assert len(campaigns) == 2

    
async def test__get_all_campaign__return_empty_list_when_no_campaigns(prepare_database, campaign_repository):  # noqa: U100
    assert await campaign_repository.get_all_campaigns() == []
    

async def test__get_all_campaign__returns_correct_entry(
    prepare_database,  # noqa: U100
    campaign_repository,
    campaign_data_factory,
    make_campaign
):
    await make_campaign(**campaign_data_factory('First Campaign'))
    await make_campaign(**campaign_data_factory('Second Campaign'))
    
    campaigns = await campaign_repository.get_all_campaigns()
    
    assert all([isinstance(campaign, CampaignOrm)for campaign in campaigns])


async def test__get_campaign__get_campaign_model(
    prepare_database,  # noqa: U100
    campaign_repository,
    campaign_data_factory, 
    make_campaign
):
    data = campaign_data_factory()
    new_campaign = await make_campaign(**data)
    
    campaign = await campaign_repository.get_campaign(new_campaign.campaign_id)
    
    assert campaign is not None
    assert isinstance(campaign, CampaignOrm)


async def test__get_campaign__return_all_fields(
    prepare_database,  # noqa: U100 
    campaign_repository,
    make_campaign, 
    campaign_data_factory
):
    new_campaign = await make_campaign(**campaign_data_factory())
    
    campaign = await campaign_repository.get_campaign(new_campaign.campaign_id)
    
    assert campaign.name == new_campaign.name
    assert campaign.content == new_campaign.content
    assert campaign.status == new_campaign.status
    assert campaign.launch_date == new_campaign.launch_date
    
    
async def test__get_campaign__exception_campaign_not_found(prepare_database, campaign_repository):  # noqa: U100
    with pytest.raises(HTTPException):
        await campaign_repository.get_campaign(1)


async def test__update_campaign__fields_changed_successfully(prepare_database, campaign_repository, make_campaign, test_session):  # noqa: U100
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
        launch_date=datetime(2025, 10, 2, 10, 0, 0)
    )
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    campaign = result.scalars().first()
    
    assert update_campaign.name == campaign.name
    assert update_campaign.content == campaign.content
    assert update_campaign.status == campaign.status
    assert update_campaign.launch_date == campaign.launch_date


async def test__update_campaign__updated_date_changed(prepare_database, campaign_repository, campaign_data_factory, make_campaign):  # noqa: U100
    new_campaign = await make_campaign(**campaign_data_factory(name='Name'))
    
    updated_campaign = await campaign_repository.update_campaign(
        new_campaign.campaign_id,
        **campaign_data_factory(name='New Name')
    )
    
    assert new_campaign.updated_at < updated_campaign.updated_at
    

async def test__update_campaign__exception_campaign_not_found(
    prepare_database,  # noqa: U100 
    campaign_repository, 
    campaign_data_factory
):
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(1, **campaign_data_factory())


async def test__update_campaign__exception_campaign_name_already_exists(
    prepare_database,  # noqa: U100 
    campaign_repository,
    campaign_data_factory
):
    first_campaign = await campaign_repository.create_campaign(**campaign_data_factory(name='First'))
    await campaign_repository.create_campaign(**campaign_data_factory(name='Second'))
    
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(first_campaign.campaign_id, **campaign_data_factory(name='Second'))
