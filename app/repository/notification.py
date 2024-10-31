from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import typing as t
from fastapi import HTTPException

from app.models import StatusNotification, NotificationOrm


class NotificationRepository:    
    async def add(
        self, status: StatusNotification, campaign_id: int, recipient_id: int, session: AsyncSession
    ) -> NotificationOrm:
        notification = NotificationOrm(status=status, campaign_id=campaign_id, recipient_id=recipient_id)
        session.add(notification)
        try:
            await session.commit()
        except IntegrityError:
            raise HTTPException(status_code=409, detail='Database data conflict, unable to create notification')
        await session.refresh(notification)
        return notification

    async def get_all(self, session: AsyncSession) -> t.Sequence[NotificationOrm]:
        query = select(NotificationOrm)
        result = await session.execute(query)
        notifications = result.scalars().all()
        return notifications

    async def get(self, notification_id: int, session: AsyncSession) -> NotificationOrm:
        notification = await session.get(NotificationOrm, notification_id)
        if notification is None:
            raise HTTPException(status_code=404, detail='Notification not found')
        return notification

    async def run(
        self, campaign_id: int, recipient_id: int, status: StatusNotification, session: AsyncSession
    ) -> NotificationOrm:
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

    async def delete(self, notification_id: int, session: AsyncSession) -> None:
        notification = await session.get(NotificationOrm, notification_id)
        if notification is None:
            raise HTTPException(status_code=404, detail='Notification not found')
        await session.delete(notification)

    async def add_many(
        self, campaign_id: int, recipients_id: list[int], session: AsyncSession
    ) -> list[NotificationOrm]:
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
