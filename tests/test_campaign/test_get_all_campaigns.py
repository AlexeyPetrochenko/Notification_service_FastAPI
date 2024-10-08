async def test__get_all_campaigns__check_count_returning_campaigns(
    prepare_database,
    campaign_repository,
    campaign_data_factory
):
    await campaign_repository.create_campaign(**campaign_data_factory(name='First Campaign'))
    await campaign_repository.create_campaign(**campaign_data_factory(name='Second Campaign'))
    
    campaigns = await campaign_repository.get_all_campaigns()
    
    assert len(campaigns) == 2

    
async def test__get_all_campaign__when_no_campaigns(prepare_database, campaign_repository):
    assert await campaign_repository.get_all_campaigns() == []
    

async def test__get_all_campaign__returns_correct_entry(prepare_database, campaign_repository, campaign_data_factory):
    new_campaign = await campaign_repository.create_campaign(**campaign_data_factory())
    
    campaigns = await campaign_repository.get_all_campaigns()
    
    assert campaigns[0].name == new_campaign.name
    assert campaigns[0].content == new_campaign.content
    assert campaigns[0].status == new_campaign.status
    assert campaigns[0].launch_date == new_campaign.launch_date
