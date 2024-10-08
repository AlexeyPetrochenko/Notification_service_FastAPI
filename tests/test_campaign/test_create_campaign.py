import pytest
from fastapi import HTTPException
from sqlalchemy import select
from datetime import datetime

from app.models import CampaignOrm


# TODO @AlexP: Как назвать тест, в котором тестируем метод класса
# TODO @AlexP: Нормально ли использовать фабрику для генерации данных
# TODO @AlexP: Несколько assert для проверки записи в БД это нормально?
async def test__create_campaign__campaign_created_success(
    prepare_database, 
    campaign_repository, 
    test_session, 
    campaign_data_factory
): 
    data = campaign_data_factory()
    
    new_campaign = await campaign_repository.create_campaign(**data)
    query = select(CampaignOrm).where(CampaignOrm.campaign_id == new_campaign.campaign_id)
    result = await test_session.execute(query)
    campaign = result.scalars().first()
        
    assert campaign is not None    
    assert campaign.name == data['name']
    assert campaign.content == data['content']
    assert campaign.status == data['status']
    assert campaign.launch_date == data['launch_date']


async def test__create_campaign__campaign_saved_correctly(prepare_database, campaign_repository, campaign_data_factory):
    data = campaign_data_factory()
    
    new_campaign = await campaign_repository.create_campaign(**data)
    
    assert isinstance(new_campaign, CampaignOrm)
    assert new_campaign.name == data['name']
    assert new_campaign.content == data['content']
    assert new_campaign.status == data['status']
    assert new_campaign.launch_date == data['launch_date']
    

async def test__create_campaign__exception_when_adding_campaign_with_taken_name(
    prepare_database, 
    campaign_repository, 
    campaign_data_factory
):
    data = campaign_data_factory()
    await campaign_repository.create_campaign(**data)
    
    with pytest.raises(HTTPException):
        await campaign_repository.create_campaign(**data)
        

async def test__create_campaign__campaign_has_creation_and_update_dates(
    prepare_database, 
    campaign_repository, 
    campaign_data_factory
):
    campaign = await campaign_repository.create_campaign(**campaign_data_factory())
    
    assert isinstance(campaign.created_at, datetime) and isinstance(campaign.updated_at, datetime)
     
