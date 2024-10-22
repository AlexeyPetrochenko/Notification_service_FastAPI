from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from dataclasses import dataclass
import typing as t
from fastapi import HTTPException

from app.models import StatusNotification, NotificationOrm


@dataclass
class NotificationRepository:
    session_maker: t.Callable[[], AsyncSession]
    
    async def create_notification(
        self, status: StatusNotification, campaign_id: int, recipient_id: int
    ) -> NotificationOrm:
        async with self.session_maker() as session:
            notification = NotificationOrm(status=status, campaign_id=campaign_id, recipient_id=recipient_id)
            session.add(notification)
            try:
                await session.commit()
            except IntegrityError:
                raise HTTPException(status_code=409, detail='Database data conflict, unable to create notification')
            await session.refresh(notification)
            return notification

    async def get_all_notifications(self) -> t.Sequence[NotificationOrm]:
        async with self.session_maker() as session:
            query = select(NotificationOrm)
            result = await session.execute(query)
            notifications = result.scalars().all()
            return notifications

    async def get_notification(self, notification_id: int) -> NotificationOrm:
        async with self.session_maker() as session:
            notification = await session.get(NotificationOrm, notification_id)
            if notification is None:
                raise HTTPException(status_code=404, detail='Notification not found')
            return notification

    async def update_notification(self, notification_id: int, status: StatusNotification) -> NotificationOrm:
        async with self.session_maker() as session:
            notification = await session.get(NotificationOrm, notification_id)
            if notification is None:
                raise HTTPException(status_code=404, detail='Notification not found')
            notification.status = status
            session.add(notification)
            await session.commit()
            await session.refresh(notification)
            return notification

    async def delete_notification(self, notification_id: int) -> None:
        async with self.session_maker() as session:
            notification = await session.get(NotificationOrm, notification_id)
            if notification is None:
                raise HTTPException(status_code=404, detail='Notification not found')
            await session.delete(notification)
