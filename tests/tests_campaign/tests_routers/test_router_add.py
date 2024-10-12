from datetime import datetime

from app.models import CampaignOrm


async def test__add__returns_corrected_status_code(mocker, async_client, campaign_data_factory):
    mock_campaign_data = CampaignOrm(
        campaign_id=1,
        **campaign_data_factory(launch_date=datetime(2024, 12, 12).isoformat()),
        created_at=datetime(2024, 10, 7, 14, 0, 0).isoformat(),
        updated_at=datetime(2024, 10, 7, 14, 0, 0).isoformat()
    )
    mocker.patch('app.repository.CampaignRepository.create_campaign', return_value=mock_campaign_data)
    
    response = await async_client.post('/', json=campaign_data_factory(launch_date=datetime(2024, 12, 12).isoformat()))
    
    assert response.status_code == 201
