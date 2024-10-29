from fastapi import APIRouter, Body, Path
import typing as t

from app.models import StatusNotification
from app.schemas import Notification
from app.repository.notification import NotificationRepository 
from app.db import AsyncSessionLocal


router = APIRouter(prefix='/notifications')
repository = NotificationRepository(AsyncSessionLocal)


@router.post('/', status_code=201)
async def add(
    status: t.Annotated[StatusNotification, Body(examples=['pending'])],
    campaign_id: t.Annotated[int, Body(examples=['1'])],
    recipient_id: t.Annotated[int, Body(examples=['4'])]
) -> Notification:
    notification = await repository.create_notification(status, campaign_id, recipient_id)
    return Notification.model_validate(notification)


@router.get('/')
async def get_all() -> list[Notification]:
    notifications = await repository.get_all_notifications()
    return [Notification.model_validate(notification) for notification in notifications]


@router.get('/{notification_id}')
async def get(notification_id: int) -> Notification:
    notification = await repository.get_notification(notification_id) 
    return Notification.model_validate(notification)


@router.post('/{campaign_id}/{recipient_id}/run')
async def run(
    campaign_id: t.Annotated[int, Path()],
    recipient_id: t.Annotated[int, Path()],
    status: t.Annotated[StatusNotification, Body(embed=True, examples=['sent'])]
) -> Notification:
    updated_notification = await repository.run_notification(campaign_id, recipient_id, status)
    return Notification.model_validate(updated_notification)


@router.delete('/{notification_id}', status_code=204)
async def delete(notification_id: int) -> None:
    await repository.delete_notification(notification_id)


@router.post('/add/many', status_code=201)
async def add_many(
    campaign_id: t.Annotated[int, Body()], 
    recipients_id: t.Annotated[list[int], Body(examples=[[1, 2, 3]])]
) -> list[Notification]:
    notifications = await repository.add_many_notifications(campaign_id, recipients_id)
    return [Notification.model_validate(notification) for notification in notifications]
