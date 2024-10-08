import pytest
from fastapi import HTTPException
from sqlalchemy import select
from app.models import CampaignOrm


async def test__delete_campaign__success_delete(
    prepare_database, 
    campaign_repository, 
    campaign_data_factory, 
    test_session
):
    new_campaign = await campaign_repository.create_campaign(**campaign_data_factory())
    
    await campaign_repository.delete_campaign(new_campaign.campaign_id)
    
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    delete_campaign = result.scalars().first()
    assert delete_campaign is None


async def test__delete_campaign__exception_campaign_not_found(prepare_database, campaign_repository):
    with pytest.raises(HTTPException):
        await campaign_repository.delete_campaign(1)
