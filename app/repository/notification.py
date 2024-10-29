from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError, InvalidRequestError
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

    async def run_notification(
        self, campaign_id: int, recipient_id: int, status: StatusNotification
    ) -> NotificationOrm:
        async with self.session_maker() as session:
            query = select(NotificationOrm).where(
                and_(
                    NotificationOrm.campaign_id == campaign_id,
                    NotificationOrm.recipient_id == recipient_id
                )
            ).with_for_update()
            result = await session.execute(query)
            try:
                notification = result.scalars().one()
            except InvalidRequestError as err:
                raise HTTPException(status_code=422, detail=f'Error receiving notification - {err}')
            notification.status = status
            session.add(notification)
            await session.commit()
            return notification

    async def delete_notification(self, notification_id: int) -> None:
        async with self.session_maker() as session:
            notification = await session.get(NotificationOrm, notification_id)
            if notification is None:
                raise HTTPException(status_code=404, detail='Notification not found')
            await session.delete(notification)

    async def add_many_notifications(self, campaign_id: int, recipients_id: list[int]) -> list[NotificationOrm]:
        async with self.session_maker() as session:
            notifications = []
            for recipient_id in recipients_id:
                notifications.append(
                    NotificationOrm(
                        campaign_id=campaign_id,
                        recipient_id=recipient_id,
                        status=StatusNotification.PENDING
                    )
                )
            session.add_all(notifications)
            await session.commit()
            return notifications
