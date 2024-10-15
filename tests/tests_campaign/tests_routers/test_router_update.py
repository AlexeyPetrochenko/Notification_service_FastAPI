from datetime import datetime
from app.models import CampaignOrm
from app.models import StatusCampaign


async def test__update__success_update_campaign(mocker, async_client, campaign_data_factory):
    mock_data_after_update = CampaignOrm(
        campaign_id=1,
        name='Update Name',
        content='Content',
        status=StatusCampaign.DONE,
        launch_date=datetime(2024, 12, 12),
        created_at=datetime(2024, 12, 10),
        updated_at=datetime(2024, 12, 11)
    )
    mocker.patch('app.repository.campaign.CampaignRepository.update_campaign', return_value=mock_data_after_update)
    
    response = await async_client.put('/1', json={
        'name': 'Update Name',
        'content': 'Content',
        'status': StatusCampaign.DONE,
        'launch_date': datetime(2024, 12, 11).isoformat()
    })
    
    assert response.status_code == 200
