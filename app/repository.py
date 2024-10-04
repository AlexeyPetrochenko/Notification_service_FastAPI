from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import datetime as dt
from typing import Sequence

from app.models import CampaignOrm, StatusCampaign
from app.db import AsyncSessionLocal


async def create_campaign(name: str, content: str, status: StatusCampaign, launch_date: dt.datetime) -> CampaignOrm:
    async with AsyncSessionLocal() as session:
        campaign_orm = CampaignOrm(name=name, content=content, status=status, launch_date=launch_date)
        session.add(campaign_orm)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400, detail="Campaign name  already exists")
        
        await session.refresh(campaign_orm)
        return campaign_orm


async def get_all_campaigns() -> Sequence[CampaignOrm]:
    async with AsyncSessionLocal() as session:
        query = select(CampaignOrm)
        result = await session.execute(query)
        campaigns_orm = result.scalars().all()
        return campaigns_orm


async def get_campaign(campaign_id: int) -> CampaignOrm:
    async with AsyncSessionLocal() as session:
        query = select(CampaignOrm).where(CampaignOrm.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign_orm = result.scalars().first()
        if campaign_orm is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign_orm


async def update_campaign(campaign_id: int, name: str, content: str, status: StatusCampaign, launch_date: dt.datetime) -> CampaignOrm:
    async with AsyncSessionLocal() as session: 
        query = select(CampaignOrm).where(CampaignOrm.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign_orm = result.scalars().first()
        if campaign_orm is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
    
# TODO @AlexP: Как лучше обновить данные модели
        campaign_orm.name = name
        campaign_orm.content = content
        campaign_orm.status = status
        campaign_orm.launch_date = launch_date
        
        session.add(campaign_orm)
        try:
            await session.commit()            
        except IntegrityError:
            await session.rollback()
            raise HTTPException(status_code=400, detail="Campaign name  already exists")
            
        await session.refresh(campaign_orm)
        return campaign_orm
        

async def delete_campaign(campaign_id: int) -> int:
    async with AsyncSessionLocal() as session:
        query = select(CampaignOrm).where(CampaignOrm.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign_orm = result.scalars().first()
        if campaign_orm is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        await session.delete(campaign_orm)
        await session.commit()
        return campaign_id





