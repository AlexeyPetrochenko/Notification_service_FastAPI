import pytest
from datetime import datetime, timedelta
import random

from app.models import CampaignOrm, StatusCampaign, StatusNotification
from app.exceptions import ConflictException, NotFoundException, NoAvailableCampaignsException


async def test__add__campaign_created_success(
    prepare_database,  # noqa: U100
    campaign_repository, 
    test_session, 
    make_campaign,
): 
    new_campaign = await campaign_repository.add(**make_campaign(), session=test_session)     
    campaign = await test_session.get(CampaignOrm, new_campaign.campaign_id)
    
    assert campaign is not None


async def test__add__new_campaign_has_status_created(prepare_database, campaign_repository, make_campaign, test_session):   # noqa: U100
    campaign = await campaign_repository.add(**make_campaign(), session=test_session)
    
    assert campaign.status == StatusCampaign.CREATED


async def test__add__exception_when_create_campaign_with_taken_name(
    prepare_database,  # noqa: U100
    campaign_repository, 
    make_campaign,
    test_session
):
    await campaign_repository.add(**make_campaign(name='Taken Name'), session=test_session)
    
    with pytest.raises(ConflictException):
        await campaign_repository.add(**make_campaign(name='Taken Name'), session=test_session)
        

async def test__add__new_campaign_has_equal_creation_and_update_dates(
    prepare_database,  # noqa: U100
    campaign_repository, 
    make_campaign,
    test_session
):
    campaign = await campaign_repository.add(**make_campaign(), session=test_session)
    
    assert campaign.updated_at == campaign.created_at


async def test__get_all__check_count_returning_campaigns(
    prepare_database,  # noqa: U100
    campaign_repository,
    make_campaign_entity,
    test_session
):
    await make_campaign_entity(name='First Campaign')
    await make_campaign_entity(name='Second Campaign')
    
    campaigns = await campaign_repository.get_all(test_session)
    
    assert len(campaigns) == 2

    
async def test__get_all__return_empty_list_when_no_campaigns(prepare_database, campaign_repository, test_session):  # noqa: U100
    assert await campaign_repository.get_all(test_session) == []


async def test__get__campaign_returned_successfully(
    prepare_database,  # noqa: U100
    campaign_repository,
    make_campaign_entity,
    test_session
):
    new_campaign = await make_campaign_entity()
    
    campaign = await campaign_repository.get(new_campaign.campaign_id, test_session)
    
    assert campaign is not None

    
async def test__get__exception_campaign_not_found(prepare_database, campaign_repository, test_session):  # noqa: U100
    nonexistent_id = random.randint(1, 10)
    with pytest.raises(NotFoundException):
        await campaign_repository.get(nonexistent_id, test_session)


async def test__update__fields_changed_successfully(prepare_database, campaign_repository, make_campaign_entity, test_session):  # noqa: U100
    data = {
        'name': 'Name',
        'content': 'Content',
        'status': StatusCampaign.CREATED,
        'launch_date': datetime.now() + timedelta(days=1)
    }
    new_campaign = await make_campaign_entity(**data)
    
    update_campaign = await campaign_repository.update(
        campaign_id=new_campaign.campaign_id,
        name='New Name',
        content='New Content',
        launch_date=datetime.now() + timedelta(days=2),
        session=test_session
    )
    campaign = await test_session.get(CampaignOrm, new_campaign.campaign_id)
    
    assert update_campaign.name == campaign.name
    assert update_campaign.content == campaign.content
    assert update_campaign.status == campaign.status
    assert update_campaign.launch_date == campaign.launch_date
    

async def test__update__exception_campaign_not_found(
    prepare_database,  # noqa: U100 
    campaign_repository, 
    make_campaign,
    test_session
):
    campaign_data = make_campaign()
    with pytest.raises(NotFoundException):
        await campaign_repository.update(
            campaign_id=7,
            name=campaign_data['name'],
            content=campaign_data['content'],
            launch_date=campaign_data['launch_date'],
            session=test_session
        )


async def test__update__exception_campaign_name_already_exists(
    prepare_database,  # noqa: U100 
    campaign_repository,
    make_campaign_entity,
    test_session,
    faker
):
    first_campaign = await make_campaign_entity(name='Name')
    await make_campaign_entity(name='Name taken')
    
    with pytest.raises(ConflictException):
        await campaign_repository.update(
            campaign_id=first_campaign.campaign_id, 
            name='Name taken',
            content=faker.text(max_nb_chars=25),
            launch_date=faker.date_time_between(start_date='now', end_date='+30d'),
            session=test_session
        )


@pytest.mark.parametrize('status_campaign', [StatusCampaign.RUNNING, StatusCampaign.FAILED, StatusCampaign.DONE])
async def test__update__prohibit_updating_campaigns_with_a_status_other_than_created(
    prepare_database,  # noqa: U100 
    campaign_repository,
    make_campaign,
    make_campaign_entity,
    status_campaign,
    test_session
):
    campaign = await make_campaign_entity(status=status_campaign)
    
    with pytest.raises(ConflictException):
        await campaign_repository.update(
            campaign_id=campaign.campaign_id, 
            **make_campaign(),
            session=test_session
        )


async def test__delete__success_delete(prepare_database, campaign_repository, test_session, make_campaign_entity):   # noqa: U100 
    campaign = await make_campaign_entity()
    
    await campaign_repository.delete(campaign.campaign_id, test_session)
    delete_campaign = await test_session.get(CampaignOrm, campaign.campaign_id)
    
    assert delete_campaign is None


async def test__delete__exception_when_campaign_not_found(prepare_database, campaign_repository, test_session, random_id):  # noqa: U100
    with pytest.raises(NotFoundException):
        await campaign_repository.delete(random_id, test_session)


async def test__run__campaign_status_updated_to_running(prepare_database, make_campaign_entity, campaign_repository, test_session):  # noqa: U100
    campaign = await make_campaign_entity(status=StatusCampaign.CREATED)
    
    await campaign_repository.run(campaign.campaign_id, test_session)
    running_campaign = await test_session.get(CampaignOrm, campaign.campaign_id)
    
    assert running_campaign.status == StatusCampaign.RUNNING


async def test__run__exception_when_campaign_id_not_found(prepare_database, campaign_repository, test_session):  # noqa: U100
    nonexistent_id = random.randint(1, 10)
    with pytest.raises(NotFoundException):
        await campaign_repository.run(nonexistent_id, test_session)
        

async def test__acquire__get_campaign_when_launch_date_arrives(
    prepare_database, campaign_repository, test_session, make_campaign_entity, minute_in_past  # noqa: U100
):
    await make_campaign_entity(launch_date=minute_in_past)

    campaign = await campaign_repository.acquire(test_session)
    
    assert campaign is not None
    assert campaign.launch_date < datetime.now()


async def test__acquire__status_changed_to_running(
    prepare_database, campaign_repository, make_campaign_entity, minute_in_past, test_session  # noqa: U100
): 
    await make_campaign_entity(launch_date=minute_in_past, status=StatusCampaign.CREATED)
    
    running_campaign = await campaign_repository.acquire(test_session)

    assert running_campaign.status == StatusCampaign.RUNNING


async def test__acquire__exception_when_no_campaign_for_launch(
    prepare_database, campaign_repository, test_session  # noqa: U100
):
    with pytest.raises(NoAvailableCampaignsException):
        await campaign_repository.acquire(test_session)
        
        
@pytest.mark.parametrize(
    'status',
    [
        StatusCampaign.RUNNING,
        StatusCampaign.FAILED,
        StatusCampaign.DONE,
    ]
)
async def test__acquire__exception_when_status_campaign_not_created(
    prepare_database, campaign_repository, test_session, make_campaign_entity, minute_in_past, status  # noqa: U100
):
    await make_campaign_entity(launch_date=minute_in_past, status=status)
    with pytest.raises(NoAvailableCampaignsException):
        await campaign_repository.acquire(test_session)


async def test__acquire__exception_when_launch_date_in_future(
    prepare_database, campaign_repository, test_session, make_campaign_entity, minute_in_future  # noqa: U100
):
    await make_campaign_entity(launch_date=minute_in_future, status=StatusCampaign.CREATED)
    with pytest.raises(NoAvailableCampaignsException):
        await campaign_repository.acquire(test_session)


async def test__complete__when_campaign_not_found_returns_none(
    prepare_database, test_session, campaign_repository  # noqa: U100
):
    assert await campaign_repository.complete(session=test_session) is None


async def test__complete__update_status_to_done_when_no_pending_notifications(
    prepare_database,  # noqa: U100
    campaign_repository,
    test_session,
    make_campaign_entity,
    make_recipient_entities,
    make_notification_entities
):
    recipients = await make_recipient_entities(4)
    campaign = await make_campaign_entity(status=StatusCampaign.RUNNING)
    await make_notification_entities(
        status=StatusNotification.DELIVERED, campaign_id=campaign.campaign_id, recipients=recipients
    )
    
    completed_campaign = await campaign_repository.complete(test_session)
    
    assert completed_campaign.status == StatusCampaign.DONE
    

async def test__complete__returns_campaign_when_no_pending_notifications(
    prepare_database,  # noqa: U100
    campaign_repository,
    test_session,
    make_campaign_entity,
    make_recipient_entities,
    make_notification_entities
):
    recipients = await make_recipient_entities(4)
    campaign = await make_campaign_entity(status=StatusCampaign.RUNNING)
    await make_notification_entities(
        status=StatusNotification.DELIVERED, campaign_id=campaign.campaign_id, recipients=recipients
    )
    
    completed_campaign = await campaign_repository.complete(test_session)
    
    assert completed_campaign is not None


async def test__complete__returns_none_when_campaign_has_pending_notifications(
    prepare_database,  # noqa: U100
    campaign_repository,
    test_session,
    make_campaign_entity,
    make_recipient_entities,
    make_notification_entities
):
    recipients = await make_recipient_entities(4)
    campaign = await make_campaign_entity(status=StatusCampaign.RUNNING)
    await make_notification_entities(
        status=StatusNotification.PENDING, campaign_id=campaign.campaign_id, recipients=recipients
    )
    
    completed_campaign = await campaign_repository.complete(test_session)
    
    assert completed_campaign is None
