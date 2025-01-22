from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import typing as t

from app.models import StatusNotification, NotificationOrm
from app.exceptions import NotFoundException, ConflictException


class NotificationRepository:    
    async def add(
        self, status: StatusNotification, campaign_id: int, recipient_id: int, session: AsyncSession
    ) -> NotificationOrm:
        notification = NotificationOrm(status=status, campaign_id=campaign_id, recipient_id=recipient_id)
        session.add(notification)
        try:
            await session.commit()
        except IntegrityError:
            raise ConflictException(
                f'Unable to create notification with [campaign_id: {campaign_id}, recipient_id: {recipient_id}]'
            )
        return notification

    async def get_all(self, session: AsyncSession) -> t.Sequence[NotificationOrm]:
        query = select(NotificationOrm)
        result = await session.execute(query)
        notifications = result.scalars().all()
        return notifications

    async def get(self, notification_id: int, session: AsyncSession) -> NotificationOrm:
        notification = await session.get(NotificationOrm, notification_id)
        if notification is None:
            raise NotFoundException(detail=f'Notification [notification_id: {notification_id}] not found')
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
        except InvalidRequestError:
            raise NotFoundException(
                detail=f'Notification [campaign_id: {campaign_id}, recipient_id: {recipient_id}] not found'
            )
        notification.status = status
        session.add(notification)
        await session.commit()
        return notification

    async def delete(self, notification_id: int, session: AsyncSession) -> None:
        notification = await session.get(NotificationOrm, notification_id)
        if notification is None:
            raise NotFoundException(detail=f'Notification [notification_id: {notification_id}] not found')
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

    async def get_notifications_by_campaign_id(
        self, campaign_id: int, session: AsyncSession
    ) -> t.Sequence[NotificationOrm]:
        query = select(NotificationOrm).where(NotificationOrm.campaign_id == campaign_id)
        result = await session.execute(query)
        notifications = result.scalars().all()
        return notifications
