from fastapi import APIRouter, Body, Path, Depends
import typing as t

from app.models import StatusNotification
from app.schemas import Notification, NotificationCreate
from app.repository.notification import NotificationRepository 
from app.db import AsyncSessionLocal
from app.dependencies import presence_in_database


router = APIRouter(prefix='/notifications')
notification_repository = NotificationRepository(AsyncSessionLocal)


@router.post('/', status_code=201)
async def add(notification_data: NotificationCreate = Depends(presence_in_database)) -> Notification:
    notification = await notification_repository.create_notification(notification_data)
    return Notification.model_validate(notification)


@router.get('/')
async def get_all() -> list[Notification]:
    notifications = await notification_repository.get_all_notifications()
    return [Notification.model_validate(notification) for notification in notifications]


@router.get('/{notification_id}')
async def get(notification_id: int) -> Notification:
    notification = await notification_repository.get_notification(notification_id) 
    return Notification.model_validate(notification)


@router.put('/{notification_id}')
async def update(
    notification_id: t.Annotated[int, Path()],
    status: t.Annotated[StatusNotification, Body(embed=True)]
) -> Notification:
    updated_notification = await notification_repository.update_notification(notification_id, status)
    return Notification.model_validate(updated_notification)


@router.delete('/{notification_id}', status_code=204)
async def delete(notification_id: int) -> None:
    await notification_repository.delete_notification(notification_id)
