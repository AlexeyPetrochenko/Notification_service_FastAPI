from datetime import datetime
from fastapi import HTTPException

from app.models import CampaignOrm, StatusCampaign


async def test__add__returns_corrected_status_code(mocker, async_client, campaign_data_factory):
    mock_campaign_data = CampaignOrm(
        campaign_id=1,
        **campaign_data_factory(launch_date=datetime(2024, 12, 12).isoformat()),
        created_at=datetime(2024, 10, 7, 14, 0, 0).isoformat(),
        updated_at=datetime(2024, 10, 7, 14, 0, 0).isoformat()
    )
    mocker.patch('app.repository.campaign.CampaignRepository.create_campaign', return_value=mock_campaign_data)
    
    response = await async_client.post('/', json=campaign_data_factory(launch_date=datetime(2024, 12, 12).isoformat()))
    
    assert response.status_code == 201


async def test__add__returns_unprocesseble_error_when_campaign_inpast(async_client, campaign_data_factory):
    response = await async_client.post('/', json=campaign_data_factory(launch_date=datetime(2023, 12, 12).isoformat()))
    
    assert response.status_code == 422


async def test__add__no_create_campaign_when_launch_date_in_the_past(mocker, async_client, campaign_data_factory):
    create_campaign_mock = mocker.patch('app.repository.campaign.CampaignRepository.create_campaign')
    
    response = await async_client.post('/', json=campaign_data_factory(launch_date=datetime(2023, 12, 12).isoformat()))
    
    assert create_campaign_mock.call_count == 0


async def test__delete__return_corrected_status_code(mocker, async_client):
    campaign_id = 1
    mocker.patch('app.repository.campaign.CampaignRepository.delete_campaign')
    
    response = await async_client.delete(f'/{campaign_id}')
    
    assert response.status_code == 204


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
    mocker.patch('app.repository.campaign.CampaignRepository.get_all_campaigns', return_value=campaigns_returned_mock)
    
    response = await async_client.get('/')
    
    assert response.status_code == 200
    

async def test__get_all_status_code_when_empty_list_campaigns(mocker, async_client):
    mocker.patch('app.repository.campaign.CampaignRepository.get_all_campaigns', return_value=[])
    
    response = await async_client.get('/')
    
    assert response.status_code == 200


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


async def test__update__success_update_campaign(mocker, async_client):
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
