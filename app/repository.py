from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import datetime as dt
from typing import Sequence, Callable
from dataclasses import dataclass

from app.models import CampaignOrm, StatusCampaign


@dataclass
class CampaignRepository:
    new_session: Callable[[], AsyncSession]
    
    async def create_campaign(self, name: str, content: str, status: StatusCampaign, launch_date: dt.datetime) -> CampaignOrm:
        async with self.new_session() as session:
            campaign_orm = CampaignOrm(name=name, content=content, status=status, launch_date=launch_date)
            session.add(campaign_orm)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=400, detail="Campaign name  already exists")
            await session.refresh(campaign_orm)
            return campaign_orm

    async def get_all_campaigns(self) -> Sequence[CampaignOrm]:
        async with self.new_session() as session:
            query = select(CampaignOrm)
            result = await session.execute(query)
            campaigns_orm = result.scalars().all()
            return campaigns_orm

    async def get_campaign(self, campaign_id: int) -> CampaignOrm:
        async with self.new_session() as session:
            query = select(CampaignOrm).where(CampaignOrm.campaign_id == campaign_id)
            result = await session.execute(query)
            campaign_orm = result.scalars().first()
            if campaign_orm is None:
                raise HTTPException(status_code=404, detail="Campaign not found")
            return campaign_orm

    async def update_campaign(self, campaign_id: int, name: str, content: str, status: StatusCampaign, launch_date: dt.datetime) -> CampaignOrm:
        async with self.new_session() as session: 
            query = select(CampaignOrm).where(CampaignOrm.campaign_id == campaign_id)
            result = await session.execute(query)
            campaign_orm = result.scalars().first()
            if campaign_orm is None:
                raise HTTPException(status_code=404, detail="Campaign not found")
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
            
    async def delete_campaign(self, campaign_id: int) -> int:
        async with self.new_session() as session:
            query = select(CampaignOrm).where(CampaignOrm.campaign_id == campaign_id)
            result = await session.execute(query)
            campaign_orm = result.scalars().first()
            if campaign_orm is None:
                raise HTTPException(status_code=404, detail="Campaign not found")
            await session.delete(campaign_orm)
            await session.commit()
            return campaign_id
