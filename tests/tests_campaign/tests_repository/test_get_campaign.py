import pytest
from fastapi import HTTPException

from app.models import CampaignOrm


async def test__get_campaign__get_campaign_model(
    prepare_database,
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
    prepare_database, 
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
    
    
async def test__get_campaign__exception_campaign_not_found(prepare_database, campaign_repository):
    with pytest.raises(HTTPException):
        await campaign_repository.get_campaign(1)
