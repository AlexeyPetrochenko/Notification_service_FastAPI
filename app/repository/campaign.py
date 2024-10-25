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
    session_maker: Callable[[], AsyncSession]
    
    async def create_campaign(self, name: str, content: str, launch_date: dt.datetime) -> CampaignOrm:
        async with self.session_maker() as session:
            campaign_orm = CampaignOrm(
                name=name, content=content, status=StatusCampaign.CREATED, launch_date=launch_date
            )
            session.add(campaign_orm)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=409, detail="Campaign name already exists")
            await session.refresh(campaign_orm)
            return campaign_orm

    async def get_all_campaigns(self) -> Sequence[CampaignOrm]:
        async with self.session_maker() as session:
            query = select(CampaignOrm)
            result = await session.execute(query)
            campaigns_orm = result.scalars().all()
            return campaigns_orm

    async def get_campaign(self, campaign_id: int) -> CampaignOrm:
        async with self.session_maker() as session:
            campaign = await session.get(CampaignOrm, campaign_id)
            if campaign is None:
                raise HTTPException(status_code=404, detail="Campaign not found")
            return campaign

    async def update_campaign(
        self, campaign_id: int, name: str, content: str, launch_date: dt.datetime
    ) -> CampaignOrm:
        async with self.session_maker() as session: 
            campaign_orm = await session.get(CampaignOrm, campaign_id)
            if campaign_orm is None:
                raise HTTPException(status_code=404, detail="Campaign not found")
            if campaign_orm.status != StatusCampaign.CREATED:
                raise HTTPException(
                    status_code=422, detail=f'Campaigns with {campaign_orm.status} status cannot be modified'
                )
            campaign_orm.name = name
            campaign_orm.content = content
            campaign_orm.launch_date = launch_date
            session.add(campaign_orm)
            try:
                await session.commit()            
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=400, detail="Campaign name already exists")
            await session.refresh(campaign_orm)
            return campaign_orm
            
    async def delete_campaign(self, campaign_id: int) -> None:
        async with self.session_maker() as session:
            campaign_orm = await session.get(CampaignOrm, campaign_id)
            if campaign_orm is None:
                raise HTTPException(status_code=404, detail="Campaign not found")
            await session.delete(campaign_orm)
            await session.commit()

    async def run_campaign(self, campaign_id: int) -> None:
        async with self.session_maker() as session:
            query = select(CampaignOrm).where(CampaignOrm.campaign_id == campaign_id).with_for_update()
            result = await session.execute(query)
            campaign = result.scalar_one_or_none()
            if campaign is None:
                raise HTTPException(status_code=404, detail="Campaign not found")
            campaign.status = StatusCampaign.RUNNING
            campaign.launch_date = dt.datetime.now()
            await session.commit()
