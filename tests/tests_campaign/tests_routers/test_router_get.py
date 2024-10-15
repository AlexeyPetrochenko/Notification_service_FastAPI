from fastapi import HTTPException
from datetime import datetime
from app.models import CampaignOrm, StatusCampaign


async def test__get__api_get_returns_correct_data(async_client, mocker):
    mock_campaign_data = CampaignOrm(
        campaign_id=1,
        name="Black Friday",
        content="Discounts up to 50%",
        status=StatusCampaign.CREATED,
        launch_date=datetime(2024, 11, 1, 12, 0, 0).isoformat(),
        created_at=datetime(2024, 10, 7, 14, 0, 0).isoformat(),
        updated_at=datetime(2024, 10, 7, 14, 0, 0).isoformat()
    )
    mocker.patch('app.repository.campaign.CampaignRepository.get_campaign', return_value=mock_campaign_data)
    
    response = await async_client.get('/1')
    json_response = response.json()
    
    assert response.status_code == 200
    assert json_response['name'] == mock_campaign_data.name
    assert json_response['content'] == mock_campaign_data.content
    assert json_response['status'] == mock_campaign_data.status
    assert json_response['launch_date'] == mock_campaign_data.launch_date
    assert json_response['created_at'] == mock_campaign_data.created_at
    assert json_response['updated_at'] == mock_campaign_data.updated_at


async def test__get__exception_then_campaign_not_found(async_client, mocker):
    mocker.patch(
        'app.repository.campaign.CampaignRepository.create_campaign',
        side_effect=HTTPException(status_code=404, detail="Campaign not found")
    )
    
    response = await async_client.get('/1')
    
    assert response.status_code == 404
    assert response.json() == {"detail": "Campaign not found"}
