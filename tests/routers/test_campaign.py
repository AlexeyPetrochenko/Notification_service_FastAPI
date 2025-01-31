async def test__add__when_success_returns_status_code_201(
    campaign_repo_add_mock, auth_client, make_campaign, minute_in_future  # noqa: U100
):
    response = await auth_client.post('/campaigns/', json={
        **make_campaign(launch_date=minute_in_future.isoformat())
    })
    assert response.status_code == 201


async def test__add__returns_error_unprocessable_entity_when_campaign_in_past(auth_client, make_campaign, minute_in_past):
    response = await auth_client.post('/campaigns/', json={
        **make_campaign(launch_date=minute_in_past.isoformat())
    })
    
    assert response.status_code == 422
    

async def test__add__mock_no_called_when_launch_date_in_the_past(campaign_repo_add_mock, auth_client, make_campaign, minute_in_past):    
    await auth_client.post('/campaigns/', json={**make_campaign(launch_date=minute_in_past.isoformat())})
    
    assert campaign_repo_add_mock.call_count == 0


async def test__add__mock_is_called_once(campaign_repo_add_mock, auth_client, make_campaign, minute_in_future):    
    await auth_client.post('/campaigns/', json={
        **make_campaign(launch_date=minute_in_future.isoformat())
    })
    
    assert campaign_repo_add_mock.call_count == 1


async def test__get_all__returns_status_code_200(auth_client, campaign_repo_get_all_mock):  # noqa: U100
    response = await auth_client.get('/campaigns/')
    
    assert response.status_code == 200
    

async def test__get_all__mock_is_called_once(auth_client, campaign_repo_get_all_mock):
    await auth_client.get('/campaigns/')
    
    assert campaign_repo_get_all_mock.call_count == 1


async def test__get__returns_status_code_200(auth_client, campaign_repo_get_mock, random_id):  # noqa: U100
    response = await auth_client.get(f'/campaigns/{random_id}')
    
    assert response.status_code == 200
    
    
async def test__get__mock_is_called_once(auth_client, campaign_repo_get_mock, random_id):
    await auth_client.get(f'/campaigns/{random_id}')

    assert campaign_repo_get_mock.call_count == 1
    

async def test__update__return_status_code_200(auth_client, make_campaign, campaign_repo_update_mock, minute_in_future):  # noqa: U100 
    response = await auth_client.put('campaigns/1', json={
        **make_campaign(launch_date=minute_in_future.isoformat())
    })
    
    assert response.status_code == 200


async def test__update__exception_then_launch_date_in_the_past(auth_client, campaign_repo_update_mock, make_campaign, minute_in_past):  # noqa: U100 
    response = await auth_client.put('/campaigns/1', json={
        **make_campaign(launch_date=minute_in_past.isoformat())
    })
    assert response.status_code == 422


async def test__update__mock_not_called_when_launch_date_in_the_past(auth_client, campaign_repo_update_mock, make_campaign, minute_in_past):  # noqa: U100
    await auth_client.put('/campaigns/1', json={
        **make_campaign(launch_date=minute_in_past.isoformat())
    })
    assert campaign_repo_update_mock.call_count == 0


async def test__update__mock_is_called_once_when_launch_date_in_future(
    auth_client,
    make_campaign,
    campaign_repo_update_mock,
    minute_in_future
):
    await auth_client.put('campaigns/1', json={
        **make_campaign(launch_date=minute_in_future.isoformat())
    })
    campaign_repo_update_mock.assert_called_once()


async def test__delete__return_corrected_status_code(auth_client, campaign_repo_delete_mock, random_id):  # noqa: U100
    response = await auth_client.delete(f'/campaigns/{random_id}')
    
    assert response.status_code == 204


async def test__delete__mock_is_called_once(auth_client, campaign_repo_delete_mock, random_id):
    await auth_client.delete(f'/campaigns/{random_id}')
    
    assert campaign_repo_delete_mock.call_count == 1
    

async def test__run__returns_status_code_204(auth_client, campaign_repo_run_mock, random_id):  # noqa: U100
    response = await auth_client.post(f'/campaigns/{random_id}/run')
    
    assert response.status_code == 204
    

async def test__run__mock_is_called_once(auth_client, campaign_repo_run_mock, random_id):
    await auth_client.post(f'/campaigns/{random_id}/run')
    
    assert campaign_repo_run_mock.call_count == 1
    
    
async def test__acquire_for_launch__mock_is_called_once(auth_client, campaign_repo_acquire_mock):
    await auth_client.post('/campaigns/acquire')
    
    assert campaign_repo_acquire_mock.call_count == 1
    
    
async def test__acquire_for_launch__returns_status_code_200(auth_client, campaign_repo_acquire_mock):  # noqa: U100
    response = await auth_client.post('/campaigns/acquire')
    
    assert response.status_code == 200
    

async def test__complete__mock_is_called_once(auth_client, campaign_service_complete_mock, random_id): 
    await auth_client.post(f'campaigns/{random_id}/complete')
    
    assert campaign_service_complete_mock.call_count == 1


async def test_complete_returns_status_code_204(auth_client, campaign_service_complete_mock, random_id):  # noqa: U100
    response = await auth_client.post(f'campaigns/{random_id}/complete')
    
    assert response.status_code == 204
