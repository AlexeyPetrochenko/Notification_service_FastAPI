from fastapi import APIRouter, Body, Path, HTTPException
import typing as t
import datetime

from app.schemas import Campaign
from app.repository.campaign import CampaignRepository
from app.db import AsyncSessionLocal


router = APIRouter(prefix='/campaigns')
campaign_repository = CampaignRepository(AsyncSessionLocal)


@router.post('/', status_code=201)
async def add(
    name: t.Annotated[str, Body(examples=['Оповещение по черной пятнице'])],
    content: t.Annotated[str, Body(examples=['Только в эту пятницу - скидки на все товары 30%!'])],
    launch_date: t.Annotated[datetime.datetime, Body(examples=['2024-10-04T16:05:16'])],
) -> Campaign:
    if launch_date < datetime.datetime.now(): 
        raise HTTPException(status_code=422, detail='Launch date must be in the future')
    campaign = await campaign_repository.create_campaign(name, content, launch_date)
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
    launch_date: t.Annotated[datetime.datetime, Body()]
) -> Campaign:
    if launch_date < datetime.datetime.now():
        raise HTTPException(status_code=422, detail='Launch date must be in the future')
    updated_campaign = await campaign_repository.update_campaign(campaign_id, name, content, launch_date) 
    return Campaign.model_validate(updated_campaign)


@router.delete('/{campaign_id}', status_code=204)
async def delete(campaign_id: int) -> None:
    await campaign_repository.delete_campaign(campaign_id)


@router.post('/{campaign_id}/run', status_code=204)
async def run(campaign_id: int) -> None:
    await campaign_repository.run_campaign(campaign_id)


@router.post('/acquire')
async def acquire_for_launch() -> Campaign:
    campaign = await campaign_repository.acquire_campaign()
    return Campaign.model_validate(campaign)
