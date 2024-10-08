from fastapi import APIRouter, Body, Path
import typing as t
import datetime

from app.models import StatusCampaign
from app.schemas import Campaign
from app.repository import CampaignRepository
from app.db import AsyncSessionLocal 


router = APIRouter(prefix='/campaigns')
campaign_repository = CampaignRepository(AsyncSessionLocal)

# TODO @AlexP: Добавить статус коды для роутов

@router.post('/')
async def add(
    name: t.Annotated[str, Body(examples=['Оповещение по черной пятнице'])],
    content: t.Annotated[str, Body(examples=['Только в эту пятницу - скидки на все товары 30%!'])],
    status: t.Annotated[StatusCampaign, Body()],
    launch_date: t.Annotated[datetime.datetime, Body(examples=['2024-10-04T16:05:16'])],
) -> Campaign:
    campaign = await campaign_repository.create_campaign(name, content, status, launch_date)
    return Campaign.model_validate(campaign)

    
@router.get('/')
async def get_all() -> list[Campaign]:
    campaigns = await campaign_repository.get_all_campaigns()
    return [Campaign.model_validate(campaign) for campaign in campaigns] 


@router.get('/{campaign_id}')
async def get(campaign_id: int) -> Campaign:
    campaign = await campaign_repository.get_campaign(campaign_id)
    return Campaign.model_validate(campaign)


@router.put('/{campaign_id}')
async def update(
    campaign_id: t.Annotated[int, Path()],
    name: t.Annotated[str, Body()],
    content: t.Annotated[str, Body()],
    status: t.Annotated[StatusCampaign, Body()],
    launch_date: t.Annotated[datetime.datetime, Body()]
) -> Campaign:
    updated_campaign_orm = await campaign_repository.update_campaign(campaign_id, name, content, status, launch_date) 
    return Campaign.model_validate(updated_campaign_orm)


# TODO @AlexP: Что возвращать при удалении кампании
@router.delete('/{campaign_id}')
async def delete(campaign_id: int) -> int:
    campaign_id = await campaign_repository.delete_campaign(campaign_id)
    return campaign_id
