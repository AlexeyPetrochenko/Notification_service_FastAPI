import pytest

from app.exceptions import NoAvailableCampaignsException


async def test__complete__exception_when_campaign_is_none(
    campaign_service, campaign_repo_complete_mock, test_session
):
    campaign_repo_complete_mock.return_value = None
    with pytest.raises(NoAvailableCampaignsException):
        await campaign_service.complete(test_session)
    
    
async def test__complete__mock_is_called_once(campaign_service, campaign_repo_complete_mock, test_session):
    await campaign_service.complete(test_session)
    
    assert campaign_repo_complete_mock.call_count == 1
