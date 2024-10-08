import pytest
from fastapi import HTTPException


# TODO @AlexP: Нормально ли использовать функции из кода для тестов (create_campaign) или лучше добавить 
# кампанию методами sqlalchemy напрямую

async def test__get_campaign__success(prepare_database, campaign_repository, campaign_data_factory):
    data = campaign_data_factory()
    new_campaign = await campaign_repository.create_campaign(**data)
    
    campaign = await campaign_repository.get_campaign(new_campaign.campaign_id)
    
    assert campaign is not None
    assert campaign.name == data['name']
    assert campaign.content == data['content']
    assert campaign.status == data['status']
    assert campaign.launch_date == data['launch_date']
    
    
async def test__get_campaign__exception_campaign_not_found(prepare_database, campaign_repository):
    with pytest.raises(HTTPException):
        await campaign_repository.get_campaign(1)
