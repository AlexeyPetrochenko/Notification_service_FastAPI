from datetime import datetime
import faker
import random


fake = faker.Faker()


async def test__add__returns_status_code_201(mocker, async_client, make_campaign, make_campaign_orm):
    mocker.patch('app.routers.campaign.campaign_repository.create_campaign', return_value=make_campaign_orm())
    
    response = await async_client.post('/campaigns/', json={
        **make_campaign(launch_date=fake.date_time_between('now', '+30d').isoformat())
    })
    
    assert response.status_code == 201


async def test__add__returns_error_unprocessable_entity_when_campaign_in_past(async_client, make_campaign):
    response = await async_client.post('/campaigns/', json={
        **make_campaign(launch_date=datetime(1900, 12, 12).isoformat())
    })
    
    assert response.status_code == 422
    assert response.json()['detail'] == 'Launch date must be in the future'


async def test__add__no_create_campaign_when_launch_date_in_the_past(mocker, async_client, make_campaign):
    create_campaign_mock = mocker.patch('app.routers.campaign.campaign_repository.create_campaign')
    
    await async_client.post('/campaigns/', json={**make_campaign(launch_date=datetime(2000, 12, 12).isoformat())})
    
    assert create_campaign_mock.call_count == 0


async def test__add__success_create_campaign(mocker, async_client, make_campaign, make_campaign_orm):
    create_campaign_mock = mocker.patch('app.routers.campaign.campaign_repository.create_campaign', return_value=make_campaign_orm())
    
    await async_client.post('/campaigns/', json={
        **make_campaign(launch_date=fake.date_time_between('now', '+30d').isoformat())
    })
    
    assert create_campaign_mock.call_count == 1


async def test__get_all__returns_status_code_200(async_client, mocker):
    mocker.patch('app.routers.campaign.campaign_repository.get_all_campaigns')
    
    response = await async_client.get('/campaigns/')
    
    assert response.status_code == 200
    

async def test__get_all__mock_is_called_once(mocker, async_client):
    mock_campaigns = mocker.patch('app.routers.campaign.campaign_repository.get_all_campaigns')
    
    await async_client.get('/campaigns/')
    
    assert mock_campaigns.call_count == 1


async def test__get__returns_status_code_200(async_client, mocker, make_campaign_orm):
    mocker.patch('app.routers.campaign.campaign_repository.get_campaign', return_value=make_campaign_orm())
    campaign_id = random.randint(1, 10)
    
    response = await async_client.get(f'/campaigns/{campaign_id}')
    
    assert response.status_code == 200
    
    
async def test__get__mock_is_called_once(mocker, async_client, make_campaign_orm):
    mock_get_campaign = mocker.patch('app.routers.campaign.campaign_repository.get_campaign', return_value=make_campaign_orm())
    campaign_id = random.randint(1, 10)
    
    await async_client.get(f'/campaigns/{campaign_id}')

    assert mock_get_campaign.call_count == 1
    

async def test__update__success_update_campaign(mocker, async_client, make_campaign, make_campaign_orm):
    mock = mocker.patch('app.routers.campaign.campaign_repository.update_campaign', return_value=make_campaign_orm())
    
    response = await async_client.put('campaigns/1', json={
        **make_campaign(launch_date=fake.date_time_between('now', '+30d').isoformat())
    })
    
    assert response.status_code == 200
    mock.assert_called_once()


async def test__update__exception_then_launch_date_in_the_past(async_client, make_campaign):
    response = await async_client.put('/campaigns/1', json={
        **make_campaign(launch_date=datetime(year=1900, month=12, day=12).isoformat())
    })
    assert response.status_code == 422


async def test__update__mock_is_called_once(async_client, make_campaign, mocker, make_campaign_orm):
    mock_update_campaign = mocker.patch('app.routers.campaign.campaign_repository.update_campaign', return_value=make_campaign_orm())
    await async_client.put('campaigns/1', json={
        **make_campaign(launch_date=fake.date_time_between('now', '+30d').isoformat())
    })
    mock_update_campaign.assert_called_once()


async def test__delete__return_corrected_status_code(mocker, async_client):
    campaign_id = random.randint(1, 10)
    mocker.patch('app.routers.campaign.campaign_repository.delete_campaign')
    
    response = await async_client.delete(f'/campaigns/{campaign_id}')
    
    assert response.status_code == 204


async def test__delete__mock_is_called_once(mocker, async_client):
    campaign_id = random.randint(1, 10)
    mock_delete_campaign = mocker.patch('app.routers.campaign.campaign_repository.delete_campaign')
    
    await async_client.delete(f'/campaigns/{campaign_id}')
    
    assert mock_delete_campaign.call_count == 1
    

async def test__run__returns_status_code_204(mocker, async_client):
    mocker.patch('app.routers.campaign.campaign_repository.run_campaign')
    
    response = await async_client.post('/campaigns/1/run')
    
    assert response.status_code == 204
    

async def test__run__mock_is_called_once(mocker, async_client):
    mock_run_campaign = mocker.patch('app.routers.campaign.campaign_repository.run_campaign')
    
    await async_client.post('/campaigns/1/run')
    
    assert mock_run_campaign.call_count == 1
    
