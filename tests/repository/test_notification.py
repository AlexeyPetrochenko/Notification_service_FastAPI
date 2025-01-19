from app.models import StatusNotification


async def test___get_notifications_by_campaign_id__returns_empty_list_when_no_notifications(
    prepare_database, notification_repository, test_session, random_id  # noqa: U100
):
    assert await notification_repository.get_notifications_by_campaign_id(random_id, test_session) == []
    
    
async def test__get_notifications_by_campaign_id__returns_only_notifications_for_given_campaign_id(
    prepare_database,  # noqa: U100
    test_session,
    notification_repository,
    make_notification_entities,
    make_campaign_entity,
    make_recipient_entities
):
    first_campaign = await make_campaign_entity()
    second_campaign = await make_campaign_entity()
    recipients = await make_recipient_entities(5)
    await make_notification_entities(StatusNotification.SENT, first_campaign.campaign_id, recipients)
    await make_notification_entities(StatusNotification.SENT, second_campaign.campaign_id, recipients)
    
    notifications = await notification_repository.get_notifications_by_campaign_id(campaign_id=first_campaign.campaign_id, session=test_session)
    
    assert len(notifications) == 5
    
    