import pytest
from fastapi import HTTPException
from datetime import datetime
from freezegun import freeze_time

from app.models import StatusCampaign



#ToDO : 3 кейса разбить
@pytest.mark.parametrize(
    'date_today_str, count_campaigns',
    [
        ('2024-10-25 11:30:00', 2), 
        ('2024-10-25 11:30:01', 2), 
        ('2024-10-25 11:31:00', 2), 
        ('2024-10-25 12:30:00', 2), 
        ('2024-10-26 11:30:00', 2), 
        ('2024-11-25 11:30:00', 2),
        ('2025-10-25 11:30:00', 2),
        ('2024-10-25 10:30:00', 1),
        ('2024-10-25 09:00:00', 1),
        ('2024-10-25 08:00:00', 0),
        ('2023-10-25 11:30:00', 0),
        ('2024-10-25 00:00:00', 0),
        
    ]
)
async def test__fetch_campaigns_to_launched__success_selected_by_launch_date_and_status_created(
    prepare_database,  # noqa: U100
    campaign_worker,
    make_campaign_entity,
    make_campaign,
    date_today_str,
    count_campaigns
):
    first_launch_date = datetime(year=2024, month=10, day=25, hour=9, minute=0, second=0)
    second_launch_date = datetime(year=2024, month=10, day=25, hour=11, minute=30, second=0)
    await make_campaign_entity(**make_campaign(launch_date=first_launch_date), status=StatusCampaign.CREATED)
    await make_campaign_entity(**make_campaign(launch_date=second_launch_date), status=StatusCampaign.CREATED)
    
    with freeze_time(date_today_str):
        campaigns = await campaign_worker.fetch_campaigns_to_launched()
        
        assert len(campaigns) == count_campaigns
    

@pytest.mark.parametrize(
    'status_campaign',
    [
        StatusCampaign.RUNNING,
        StatusCampaign.FAILED,
        StatusCampaign.DONE,
    ]
)
@freeze_time('2024-10-25 11:30:00')
async def test__fetch_campaigns_to_launched__when_status_not_created(
    prepare_database,  # noqa: U100
    campaign_worker,
    make_campaign,
    make_campaign_entity,
    status_campaign
):
    launch_date = datetime(year=2024, month=10, day=25, hour=9, minute=0, second=0)
    await make_campaign_entity(**make_campaign(launch_date=launch_date), status=status_campaign)
    
    campaigns = await campaign_worker.fetch_campaigns_to_launched()
    
    assert len(campaigns) == 0
    

async def test__fetch_campaigns_to_launched__returns_empty_list_when_no_campaigns(prepare_database, campaign_worker):  # noqa: U100 
    await campaign_worker.fetch_campaigns_to_launched() == []
    

async def test__fetch_recipients__mock_is_called_once_when_status_code_200(mocker, campaign_worker):
    mock_api_get_all_recipient = mocker.patch('app.workers.campaign_worker.AsyncClient.get', return_value=mocker.Mock(status_code=200)) 
    
    await campaign_worker.fetch_recipients()
    
    assert mock_api_get_all_recipient.call_count == 1
    

@pytest.mark.parametrize('status_code', [404, 500, 400])
async def test__fetch_recipients__raise_when_status_code_api_get_all_recipients_not_200(
    mocker, campaign_worker, status_code
):
    mocker.patch('app.workers.campaign_worker.AsyncClient.get', return_value=mocker.Mock(status_code=status_code)) 
    
    with pytest.raises(HTTPException):
        await campaign_worker.fetch_recipients()


# async def test__acquire_campaign_for_launch__success_returns_campaign():