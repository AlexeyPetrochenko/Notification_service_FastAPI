import random


async def test__add__when_success_returns_status_code_201(mocker, async_client, make_campaign, make_campaign_orm, minute_in_future):
    mocker.patch('app.routers.campaign.CampaignRepository.add', return_value=make_campaign_orm())
    
    response = await async_client.post('/campaigns/', json={
        **make_campaign(launch_date=minute_in_future.isoformat())
    })
    
    assert response.status_code == 201


async def test__add__returns_error_unprocessable_entity_when_campaign_in_past(async_client, make_campaign, minute_in_past):
    response = await async_client.post('/campaigns/', json={
        **make_campaign(launch_date=minute_in_past.isoformat())
    })
    
    assert response.status_code == 422
    assert response.json()['detail'] == 'Launch date must be in the future'


async def test__add__mock_no_called_when_launch_date_in_the_past(mocker, async_client, make_campaign, minute_in_past):
    create_campaign_mock = mocker.patch('app.routers.campaign.CampaignRepository.add')
    
    await async_client.post('/campaigns/', json={**make_campaign(launch_date=minute_in_past.isoformat())})
    
    assert create_campaign_mock.call_count == 0


async def test__add__mock_is_called_once(mocker, async_client, make_campaign, make_campaign_orm, minute_in_future):
    create_campaign_mock = mocker.patch('app.routers.campaign.CampaignRepository.add', return_value=make_campaign_orm())
    
    await async_client.post('/campaigns/', json={
        **make_campaign(launch_date=minute_in_future.isoformat())
    })
    
    assert create_campaign_mock.call_count == 1


async def test__get_all__returns_status_code_200(async_client, mocker):
    mocker.patch('app.routers.campaign.CampaignRepository.get_all')
    
    response = await async_client.get('/campaigns/')
    
    assert response.status_code == 200
    

async def test__get_all__mock_is_called_once(mocker, async_client):
    mock_campaigns = mocker.patch('app.routers.campaign.CampaignRepository.get_all')
    
    await async_client.get('/campaigns/')
    
    assert mock_campaigns.call_count == 1


async def test__get__returns_status_code_200(async_client, mocker, make_campaign_orm):
    mocker.patch('app.routers.campaign.CampaignRepository.get', return_value=make_campaign_orm())
    campaign_id = random.randint(1, 10)
    
    response = await async_client.get(f'/campaigns/{campaign_id}')
    
    assert response.status_code == 200
    
    
async def test__get__mock_is_called_once(mocker, async_client, make_campaign_orm):
    mock_get_campaign = mocker.patch('app.routers.campaign.CampaignRepository.get', return_value=make_campaign_orm())
    campaign_id = random.randint(1, 10)
    
    await async_client.get(f'/campaigns/{campaign_id}')

    assert mock_get_campaign.call_count == 1
    

async def test__update__success_update_campaign(mocker, async_client, make_campaign, make_campaign_orm, minute_in_future):
    mock = mocker.patch('app.routers.campaign.CampaignRepository.update', return_value=make_campaign_orm())
    
    response = await async_client.put('campaigns/1', json={
        **make_campaign(launch_date=minute_in_future.isoformat())
    })
    
    assert response.status_code == 200
    mock.assert_called_once()


async def test__update__exception_then_launch_date_in_the_past(async_client, make_campaign, minute_in_past):
    response = await async_client.put('/campaigns/1', json={
        **make_campaign(launch_date=minute_in_past.isoformat())
    })
    assert response.status_code == 422


async def test__update__mock_is_called_once(async_client, make_campaign, mocker, make_campaign_orm, minute_in_future):
    mock_update_campaign = mocker.patch('app.routers.campaign.CampaignRepository.update', return_value=make_campaign_orm())
    await async_client.put('campaigns/1', json={
        **make_campaign(launch_date=minute_in_future.isoformat())
    })
    mock_update_campaign.assert_called_once()


async def test__delete__return_corrected_status_code(mocker, async_client):
    campaign_id = random.randint(1, 10)
    mocker.patch('app.routers.campaign.CampaignRepository.delete')
    
    response = await async_client.delete(f'/campaigns/{campaign_id}')
    
    assert response.status_code == 204


async def test__delete__mock_is_called_once(mocker, async_client):
    campaign_id = random.randint(1, 10)
    mock_delete_campaign = mocker.patch('app.routers.campaign.CampaignRepository.delete')
    
    await async_client.delete(f'/campaigns/{campaign_id}')
    
    assert mock_delete_campaign.call_count == 1
    

async def test__run__returns_status_code_204(mocker, async_client):
    mocker.patch('app.routers.campaign.CampaignRepository.run')
    
    response = await async_client.post('/campaigns/1/run')
    
    assert response.status_code == 204
    

async def test__run__mock_is_called_once(mocker, async_client):
    mock_run_campaign = mocker.patch('app.routers.campaign.CampaignRepository.run')
    
    await async_client.post('/campaigns/1/run')
    
    assert mock_run_campaign.call_count == 1
    
    
async def test__acquire_for_launch__mock_is_called_once(mocker, async_client, make_campaign_orm):
    mock_acquire_campaign = mocker.patch('app.routers.campaign.CampaignRepository.acquire', return_value=make_campaign_orm())
    
    await async_client.post('/campaigns/acquire')
    
    assert mock_acquire_campaign.call_count == 1
    
    
async def test__acquire_for_launch__returns_status_code_200(mocker, async_client, make_campaign_orm):
    mocker.patch('app.routers.campaign.CampaignRepository.acquire', return_value=make_campaign_orm())
    
    response = await async_client.post('/campaigns/acquire')
    
    assert response.status_code == 200
    
