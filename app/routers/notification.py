from typing import Annotated
from fastapi import APIRouter, Body, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import StatusNotification
from app.schemas import Notification
from app.repository.notification import NotificationRepository 
from app.db import get_db_session
from app.dependencies import get_current_user


router = APIRouter(prefix='/notifications', dependencies=[Depends(get_current_user)])


def get_repository_notification() -> NotificationRepository:
    return NotificationRepository()


@router.post('/', status_code=201)
async def add(
    status: Annotated[StatusNotification, Body(examples=['pending'])],
    campaign_id: Annotated[int, Body(examples=['1'])],
    recipient_id: Annotated[int, Body(examples=['4'])],
    session: AsyncSession = Depends(get_db_session), 
    repository: NotificationRepository = Depends(get_repository_notification)
) -> Notification:
    notification = await repository.add(status, campaign_id, recipient_id, session)
    return Notification.model_validate(notification)


@router.get('/')
async def get_all(
    session: AsyncSession = Depends(get_db_session), 
    repository: NotificationRepository = Depends(get_repository_notification)
) -> list[Notification]:
    notifications = await repository.get_all(session)
    return [Notification.model_validate(notification) for notification in notifications]


@router.get('/{notification_id}')
async def get(
    notification_id: int,
    session: AsyncSession = Depends(get_db_session), 
    repository: NotificationRepository = Depends(get_repository_notification)
) -> Notification:
    notification = await repository.get(notification_id, session) 
    return Notification.model_validate(notification)


@router.post('/{campaign_id}/recipients/{recipient_id}/run')
async def run(
    campaign_id: Annotated[int, Path()],
    recipient_id: Annotated[int, Path()],
    status: Annotated[StatusNotification, Body(embed=True, examples=['sent'])],
    session: AsyncSession = Depends(get_db_session), 
    repository: NotificationRepository = Depends(get_repository_notification)
) -> Notification:
    updated_notification = await repository.run(campaign_id, recipient_id, status, session)
    return Notification.model_validate(updated_notification)


@router.delete('/{notification_id}', status_code=204)
async def delete(
    notification_id: int,
    session: AsyncSession = Depends(get_db_session), 
    repository: NotificationRepository = Depends(get_repository_notification)
) -> None:
    await repository.delete(notification_id, session)


@router.post('/add/many', status_code=201)
async def add_many(
    campaign_id: Annotated[int, Body()], 
    recipients_id: Annotated[list[int], Body(examples=[[1, 2, 3]])],
    session: AsyncSession = Depends(get_db_session), 
    repository: NotificationRepository = Depends(get_repository_notification)
) -> list[Notification]:
    notifications = await repository.add_many(campaign_id, recipients_id, session)
    return [Notification.model_validate(notification) for notification in notifications]
