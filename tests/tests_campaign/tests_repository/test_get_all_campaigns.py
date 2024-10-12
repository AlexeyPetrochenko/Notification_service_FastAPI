from app.models import CampaignOrm


async def test__get_all_campaigns__check_count_returning_campaigns(
    prepare_database,
    campaign_repository,
    campaign_data_factory,
    make_campaign
):
    await make_campaign(**campaign_data_factory(name='First Campaign'))
    await make_campaign(**campaign_data_factory(name='Second Campaign'))
    
    campaigns = await campaign_repository.get_all_campaigns()
    
    assert len(campaigns) == 2

    
async def test__get_all_campaign__return_empty_list_when_no_campaigns(prepare_database, campaign_repository):
    assert await campaign_repository.get_all_campaigns() == []
    

async def test__get_all_campaign__returns_correct_entry(
    prepare_database,
    campaign_repository,
    campaign_data_factory,
    make_campaign
):
    await make_campaign(**campaign_data_factory('First Campaign'))
    await make_campaign(**campaign_data_factory('Second Campaign'))
    
    campaigns = await campaign_repository.get_all_campaigns()
    
    assert all([isinstance(campaign, CampaignOrm)for campaign in campaigns])
