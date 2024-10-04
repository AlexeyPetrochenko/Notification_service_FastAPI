from fastapi import APIRouter, Body, Path
import typing as t
import datetime

from app.models import StatusCampaign, CampaignOrm
from app.schemas import CampaignSC
from app import repository


router = APIRouter(prefix='/campaigns')


@router.post('/')
async def add(
    name: t.Annotated[str, Body(examples=['Оповещение по черной пятнице'])],
    content: t.Annotated[str, Body(examples=['Только в эту пятницу - скидки на все товары 30%!'])],
    status: t.Annotated[StatusCampaign, Body()],
    launch_date: t.Annotated[datetime.datetime, Body(examples=['2024-10-04T16:05:16'])],
) -> CampaignSC:
    
    new_campaign_orm: CampaignOrm = await repository.create_campaign(name, content, status, launch_date)
    new_campaign: CampaignSC = CampaignSC.model_validate(new_campaign_orm)
    return new_campaign


# TODO @AlexP: Вернуть объект Alchemy
# TODO @AlexP: Конвертнуть модель алхимии в схему ответа from_orm()
# TODO @AlexP: Вернуть объект схему кампании
    
    
@router.get('/')
async def get_all() -> list[CampaignSC]:
    campaigns_orm = await repository.get_all_campaigns()
    campaigns = [CampaignSC.model_validate(campaign) for campaign in campaigns_orm] 
    return campaigns


@router.get('/{campaign_id}')
async def get(campaign_id: int) -> CampaignSC:
    campaign_orm = await repository.get_campaign(campaign_id)
    campaign = CampaignSC.model_validate(campaign_orm)
    return campaign


@router.put('/{campaign_id}')
async def update(
    campaign_id: t.Annotated[int, Path()],
    name: t.Annotated[str, Body()],
    content: t.Annotated[str, Body()],
    status: t.Annotated[StatusCampaign, Body()],
    launch_date: t.Annotated[datetime.datetime, Body()]
) -> CampaignSC:
    updated_campaign_orm = await repository.update_campaign(campaign_id, name, content, status, launch_date) 
    updated_campaign = CampaignSC.model_validate(updated_campaign_orm)
    return updated_campaign


# TODO @AlexP: Что возвращать при удалении кампании
@router.delete('/{campaign_id}')
async def delete(campaign_id: int) -> int:
    campaign_id = await repository.delete_campaign(campaign_id)
    return campaign_id
