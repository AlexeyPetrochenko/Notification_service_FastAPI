from datetime import datetime

from app.models import CampaignOrm


async def test__get_all__returns_corrected_status_code(async_client, mocker, campaign_data_factory):
    campaigns_returned_mock = [
        CampaignOrm(
            campaign_id=1,
            **campaign_data_factory(name='First Name'),
            created_at=datetime(2024, 12, 12), 
            updated_at=datetime(2024, 12, 12)
        ),
        CampaignOrm(
            campaign_id=2,
            **campaign_data_factory(name='Second Name'),
            created_at=datetime(2024, 12, 12),
            updated_at=datetime(2024, 12, 12)
        )
    ]
    mocker.patch('app.repository.CampaignRepository.get_all_campaigns', return_value=campaigns_returned_mock)
    
    response = await async_client.get('/')
    
    assert response.status_code == 200
    

async def test__get_all_status_code_when_empty_list_campaigns(mocker, async_client):
    mocker.patch('app.repository.CampaignRepository.get_all_campaigns', return_value=[])
    
    response = await async_client.get('/')
    
    assert response.status_code == 200
