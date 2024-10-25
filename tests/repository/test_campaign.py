import pytest
from fastapi import HTTPException
from sqlalchemy import select
from datetime import datetime, timedelta
import faker
import random

from app.models import CampaignOrm, StatusCampaign


fake = faker.Faker()


async def test__create_campaign__campaign_created_success(
    prepare_database,  # noqa: U100
    campaign_repository, 
    test_session, 
    make_campaign,
): 
    new_campaign = await campaign_repository.create_campaign(**make_campaign())     
    campaign = await test_session.get(CampaignOrm, new_campaign.campaign_id)
    
    assert campaign is not None


async def test__create_campaign__returning_value_orm(prepare_database, campaign_repository, make_campaign):  # noqa: U100
    campaign = await campaign_repository.create_campaign(**make_campaign())
    
    assert isinstance(campaign, CampaignOrm)


async def test__create_campaign__new_campaign_has_status_created(prepare_database, campaign_repository, make_campaign):   # noqa: U100
    campaign = await campaign_repository.create_campaign(**make_campaign())
    
    assert campaign.status == StatusCampaign.CREATED


async def test__create_campaign__exception_when_create_campaign_with_taken_name(
    prepare_database,  # noqa: U100
    campaign_repository, 
    make_campaign
):
    await campaign_repository.create_campaign(**make_campaign(name='Taken Name'))
    
    with pytest.raises(HTTPException):
        await campaign_repository.create_campaign(**make_campaign(name='Taken Name'))
        

async def test__create_campaign__campaign_has_creation_and_update_dates(
    prepare_database,  # noqa: U100
    campaign_repository, 
    make_campaign
):
    campaign = await campaign_repository.create_campaign(**make_campaign())
    
    assert isinstance(campaign.created_at, datetime) and isinstance(campaign.updated_at, datetime)


async def test__get_all_campaigns__check_count_returning_campaigns(
    prepare_database,  # noqa: U100
    campaign_repository,
    make_campaign,
    make_campaign_entity
):
    await make_campaign_entity(**make_campaign(name='First Campaign'))
    await make_campaign_entity(**make_campaign(name='Second Campaign'))
    
    campaigns = await campaign_repository.get_all_campaigns()
    
    assert len(campaigns) == 2

    
async def test__get_all_campaign__return_empty_list_when_no_campaigns(prepare_database, campaign_repository):  # noqa: U100
    assert await campaign_repository.get_all_campaigns() == []
    

async def test__get_all_returns_values_list_of_orm_models(
    prepare_database,  # noqa: U100
    campaign_repository,
    make_campaign,
    make_campaign_entity
):
    await make_campaign_entity(**make_campaign('First Campaign'))
    await make_campaign_entity(**make_campaign('Second Campaign'))
    
    campaigns = await campaign_repository.get_all_campaigns()
    
    assert all([isinstance(campaign, CampaignOrm)for campaign in campaigns]) and isinstance(campaigns, list) 


async def test__get_campaign__campaign_returned_successfully(
    prepare_database,  # noqa: U100
    campaign_repository,
    make_campaign, 
    make_campaign_entity
):
    new_campaign = await make_campaign_entity(**make_campaign())
    
    campaign = await campaign_repository.get_campaign(new_campaign.campaign_id)
    
    assert campaign is not None
    assert isinstance(campaign, CampaignOrm)
    
    
async def test__get_campaign__exception_campaign_not_found(prepare_database, campaign_repository):  # noqa: U100
    nonexistent_id = random.randint(1, 10)
    with pytest.raises(HTTPException):
        await campaign_repository.get_campaign(nonexistent_id)


async def test__update_campaign__fields_changed_successfully(prepare_database, campaign_repository, make_campaign_entity, test_session):  # noqa: U100
    data = {
        'name': 'Name',
        'content': 'Content',
        'status': StatusCampaign.CREATED,
        'launch_date': datetime.now() + timedelta(days=1)
    }
    new_campaign = await make_campaign_entity(**data)
    
    update_campaign = await campaign_repository.update_campaign(
        campaign_id=new_campaign.campaign_id,
        name='New Name',
        content='New Content',
        launch_date=datetime.now() + timedelta(days=2)
    )
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    campaign = result.scalars().first()
    
    assert update_campaign.name == campaign.name
    assert update_campaign.content == campaign.content
    assert update_campaign.status == campaign.status
    assert update_campaign.launch_date == campaign.launch_date
    

async def test__update_campaign__exception_campaign_not_found(
    prepare_database,  # noqa: U100 
    campaign_repository, 
    make_campaign
):
    campaign_data = make_campaign()
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(
            campaign_id=7,
            name=campaign_data['name'],
            content=campaign_data['content'],
            launch_date=campaign_data['launch_date']
        )


async def test__update_campaign__exception_campaign_name_already_exists(
    prepare_database,  # noqa: U100 
    campaign_repository,
    make_campaign
):
    first_campaign = await campaign_repository.create_campaign(**make_campaign(name='Name'))
    await campaign_repository.create_campaign(**make_campaign(name='Name taken'))
    
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(
            campaign_id=first_campaign.campaign_id, 
            name='Name taken',
            content=fake.text(max_nb_chars=25),
            launch_date=fake.date_time_between(start_date='now', end_date='+30d')
        )


async def test__update_campaign__prohibit_updating_campaigns_with_a_status_other_than_created(
    prepare_database,  # noqa: U100 
    campaign_repository,
    make_campaign,
    make_campaign_entity
):
    launched_campaign = await make_campaign_entity(**make_campaign(), status=StatusCampaign.RUNNING)
    failed_campaign = await make_campaign_entity(**make_campaign(), status=StatusCampaign.FAILED)
    completed_campaign = await make_campaign_entity(**make_campaign(), status=StatusCampaign.DONE)
    
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(
            campaign_id=launched_campaign.campaign_id, 
            **make_campaign(),
        )
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(
            campaign_id=failed_campaign.campaign_id, 
            **make_campaign(),
        )
    with pytest.raises(HTTPException):
        await campaign_repository.update_campaign(
            campaign_id=completed_campaign.campaign_id, 
            **make_campaign(),
        )


async def test__delete_campaign__success_delete(
    prepare_database,  # noqa: U100 
    campaign_repository, 
    make_campaign, 
    test_session,
    make_campaign_entity
):
    campaign = await make_campaign_entity(**make_campaign())
    
    await campaign_repository.delete_campaign(campaign.campaign_id)
    delete_campaign = await test_session.get(CampaignOrm, campaign.campaign_id)
    
    assert delete_campaign is None


async def test__delete_campaign__exception_campaign_not_found(prepare_database, campaign_repository):  # noqa: U100
    nonexistent_id = random.randint(1, 10)
    with pytest.raises(HTTPException):
        await campaign_repository.delete_campaign(nonexistent_id)


async def test__run_campaign__campaign_status_updated_to_running(prepare_database, make_campaign, make_campaign_entity, campaign_repository, test_session):  # noqa: U100
    campaign = await make_campaign_entity(**make_campaign(), status=StatusCampaign.CREATED)
    
    await campaign_repository.run_campaign(campaign.campaign_id)
    running_campaign = await test_session.get(CampaignOrm, campaign.campaign_id)
    
    assert running_campaign.status == StatusCampaign.RUNNING


async def test__run_campaign__exception_when_campaign_id_not_found(prepare_database, campaign_repository):  # noqa: U100
    nonexistent_id = random.randint(1, 10)
    with pytest.raises(HTTPException):
        await campaign_repository.run_campaign(nonexistent_id)
