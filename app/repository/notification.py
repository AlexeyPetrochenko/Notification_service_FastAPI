from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dataclasses import dataclass
import typing as t
from fastapi import HTTPException

from app.models import StatusNotification, NotificationOrm
from app.schemas import NotificationCreate


@dataclass
class NotificationRepository:
    session_maker: t.Callable[[], AsyncSession]
    
    async def create_notification(self, notification_data: NotificationCreate) -> NotificationOrm:
        async with self.session_maker() as session:
            notification = NotificationOrm(**notification_data.model_dump())
            session.add(notification)
            await session.commit()
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
            