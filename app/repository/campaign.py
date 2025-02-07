from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime 
from typing import Sequence

from app.models import CampaignOrm, StatusCampaign, NotificationOrm, StatusNotification
from app.exceptions import ConflictException, NotFoundException, NoAvailableCampaignsException


class CampaignRepository:
    async def add(
        self, name: str, content: str, launch_date: datetime, session: AsyncSession
    ) -> CampaignOrm:
        campaign_orm = CampaignOrm(
            name=name, content=content, status=StatusCampaign.CREATED, launch_date=launch_date
        )
        session.add(campaign_orm)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ConflictException(f'Campaign [name: {name}], already exists')
        return campaign_orm

    async def get_all(self, session: AsyncSession) -> Sequence[CampaignOrm]:
        query = select(CampaignOrm)
        result = await session.execute(query)
        campaigns_orm = result.scalars().all()
        return campaigns_orm

    async def get(self, campaign_id: int, session: AsyncSession) -> CampaignOrm | None:
        campaign = await session.get(CampaignOrm, campaign_id)
        if campaign is None:
            raise NotFoundException(detail=f"Campaign with [id: {campaign_id}] not found")
        return campaign
    
    async def update(
        self, campaign_id: int, name: str, content: str, launch_date: datetime, session: AsyncSession
    ) -> CampaignOrm:
        campaign_orm = await session.get(CampaignOrm, campaign_id)
        if campaign_orm is None:
            raise NotFoundException(detail=f"Campaign with [id: {campaign_id}] not found")
        if campaign_orm.status != StatusCampaign.CREATED:
            raise ConflictException(f'Campaigns with {campaign_orm.status} status cannot be modified')
        campaign_orm.name = name
        campaign_orm.content = content
        campaign_orm.launch_date = launch_date
        session.add(campaign_orm)
        try:
            await session.commit()            
        except IntegrityError:
            await session.rollback()
            raise ConflictException(f'Campaign [name: {name}], already exists')
        return campaign_orm
            
    async def delete(self, campaign_id: int, session: AsyncSession) -> None:
        campaign_orm = await session.get(CampaignOrm, campaign_id)
        if campaign_orm is None:
            raise NotFoundException(detail=f"Campaign with [id: {campaign_id}] not found")
        await session.delete(campaign_orm)
        await session.commit()

    async def run(self, campaign_id: int, session: AsyncSession) -> None:
        query = select(CampaignOrm).where(CampaignOrm.campaign_id == campaign_id).with_for_update()
        result = await session.execute(query)
        campaign = result.scalar_one_or_none()
        if campaign is None:
            raise NotFoundException(detail=f"Campaign with [id: {campaign_id}] not found")
        campaign.status = StatusCampaign.RUNNING
        campaign.launch_date = datetime.now()
        await session.commit()

    async def acquire(self, session: AsyncSession) -> CampaignOrm:
        query = select(CampaignOrm).where(
            and_(
                CampaignOrm.launch_date <= datetime.now(),
                CampaignOrm.status == StatusCampaign.CREATED
            )
        ).with_for_update()
        result = await session.execute(query)
        campaign = result.scalars().first()
        if not campaign:
            raise NoAvailableCampaignsException(detail='No available campaigns for launch')
        campaign.status = StatusCampaign.RUNNING
        await session.commit()
        return campaign

    async def complete(self, session: AsyncSession) -> CampaignOrm | None:
        query = (
            select(CampaignOrm)
            .where(CampaignOrm.status == StatusCampaign.RUNNING)
            .where(~CampaignOrm.notifications.any(NotificationOrm.status == StatusNotification.PENDING))
        ).with_for_update()
        result = await session.execute(query)
        campaign = result.scalars().first()
        if not campaign:
            return None
        campaign.status = StatusCampaign.DONE
        await session.commit()
        return campaign
        
        
