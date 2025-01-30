import typing as t
import datetime
from fastapi import APIRouter, Body, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import Campaign
from app.repository.campaign import CampaignRepository
from app.service.campaign import CampaignService
from app.db import get_db_session
from app.exceptions import LaunchDateException
from app.dependencies import get_campaign_repository, get_campaign_service


router = APIRouter(prefix='/campaigns')


@router.post('/', status_code=201)
async def add(
    name: t.Annotated[str, Body(examples=['Оповещение по черной пятнице'])],
    content: t.Annotated[str, Body(examples=['Только в эту пятницу - скидки на все товары 30%!'])],
    launch_date: t.Annotated[datetime.datetime, Body(examples=['2024-10-04T16:05:16'])],
    session: AsyncSession = Depends(get_db_session),
    repository: CampaignRepository = Depends(get_campaign_repository)
) -> Campaign:
    if launch_date < datetime.datetime.now(): 
        raise LaunchDateException(launch_date=launch_date)
    campaign = await repository.add(name, content, launch_date, session)
    return Campaign.model_validate(campaign)


@router.get('/')
async def get_all(
    session: AsyncSession = Depends(get_db_session),
    repository: CampaignRepository = Depends(get_campaign_repository)
) -> list[Campaign]:
    campaigns = await repository.get_all(session)
    return [Campaign.model_validate(campaign) for campaign in campaigns] 


@router.get('/{campaign_id}')
async def get(
    campaign_id: int, 
    session: AsyncSession = Depends(get_db_session),
    repository: CampaignRepository = Depends(get_campaign_repository)
) -> Campaign:
    campaign = await repository.get(campaign_id, session)
    return Campaign.model_validate(campaign)


@router.put('/{campaign_id}')
async def update(
    campaign_id: t.Annotated[int, Path()],
    name: t.Annotated[str, Body()],
    content: t.Annotated[str, Body()],
    launch_date: t.Annotated[datetime.datetime, Body()],
    session: AsyncSession = Depends(get_db_session),
    repository: CampaignRepository = Depends(get_campaign_repository)
) -> Campaign:
    if launch_date < datetime.datetime.now():
        raise LaunchDateException(launch_date=launch_date)
    updated_campaign = await repository.update(campaign_id, name, content, launch_date, session) 
    return Campaign.model_validate(updated_campaign)


@router.delete('/{campaign_id}', status_code=204)
async def delete(
    campaign_id: int, session: AsyncSession = Depends(get_db_session),
    repository: CampaignRepository = Depends(get_campaign_repository)
) -> None:
    await repository.delete(campaign_id, session)


@router.post('/{campaign_id}/run', status_code=204)
async def run(
    campaign_id: int, session: AsyncSession = Depends(get_db_session),
    repository: CampaignRepository = Depends(get_campaign_repository)
) -> None:
    await repository.run(campaign_id, session)


@router.post('/acquire')
async def acquire_for_launch(
    session: AsyncSession = Depends(get_db_session),
    repository: CampaignRepository = Depends(get_campaign_repository)
) -> Campaign:
    campaign = await repository.acquire(session)
    return Campaign.model_validate(campaign)


@router.post('/{campaign_id}/complete', status_code=204)
async def complete(
    campaign_id: int,
    session: t.Annotated[AsyncSession, Depends(get_db_session)],
    service: t.Annotated[CampaignService, Depends(get_campaign_service)],
) -> None:
    await service.complete(campaign_id, session)
