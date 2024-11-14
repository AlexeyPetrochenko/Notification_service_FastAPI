from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime 
from typing import Sequence
from collections import Counter

from app.models import CampaignOrm, StatusCampaign, StatusNotification
from app.exceptions import ConflictException, NotFoundException, NoCampaignsAvailableException


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

    async def get(self, campaign_id: int, session: AsyncSession) -> CampaignOrm:
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
            raise NoCampaignsAvailableException()
        campaign.status = StatusCampaign.RUNNING
        await session.commit()
        return campaign
    
    async def complete(self, campaign_id: int, session: AsyncSession) -> None:
        query = select(CampaignOrm).options(
            selectinload(CampaignOrm.notifications)
        ).where(CampaignOrm.campaign_id == campaign_id)
        result = await session.execute(query)
        campaign = result.scalars().first()
        
        if campaign is None:
            raise NotFoundException(f'Campaign with [id: {campaign_id}] not found')
        if campaign.status != StatusCampaign.RUNNING:
            raise ConflictException(f'Campaigns with [status: {campaign.status}] cannot be completion')
        
        notifications_statistic = Counter([notification.status for notification in campaign.notifications])
        try:
            percentage_delivered = (
                notifications_statistic[StatusNotification.DELIVERED] / notifications_statistic.total() * 100
            )
        except ZeroDivisionError:
            raise NotFoundException(f'There are no notifications in this campaign [id: {campaign_id}].')
        
        if percentage_delivered > 80:
            campaign.status = StatusCampaign.DONE
        else:
            campaign.status = StatusCampaign.FAILED
        
        await session.commit()
