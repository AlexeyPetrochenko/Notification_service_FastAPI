async def test__delete__return_corrected_status_code(mocker, campaign_repository, async_client):
    campaign_id = 1
    mocker.patch('app.repository.CampaignRepository.delete_campaign')
    
    response = await async_client.delete(f'/{campaign_id}')
    
    assert response.status_code == 204
