import typing as t
from fastapi import APIRouter, Body, Path, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr

from app.schemas import Recipient
from app.db import get_db_session
from app.repository.recipient import RecipientRepository


router = APIRouter(prefix='/recipients')


def get_repository() -> RecipientRepository:
    return RecipientRepository()


@router.post('/', status_code=201)
async def add(
    name: t.Annotated[str, Body(examples=['Julia'])],
    lastname: t.Annotated[str, Body(examples=['Roberts'])],
    age: t.Annotated[int, Body(examples=[56], lt=100)],
    contact_email: t.Annotated[EmailStr, Body(examples=['julia@example.com'])],
    session: AsyncSession = Depends(get_db_session),
    repository: RecipientRepository = Depends(get_repository)
) -> Recipient:
    recipient = await repository.add(name, lastname, age, contact_email, session)
    return Recipient.model_validate(recipient)


@router.get('/')
async def get_all(
    session: AsyncSession = Depends(get_db_session),
    repository: RecipientRepository = Depends(get_repository)
) -> list[Recipient]:
    recipients = await repository.get_all(session)
    return [Recipient.model_validate(recipient) for recipient in recipients]


@router.get('/{recipient_id}')
async def get(
    recipient_id: int,
    session: AsyncSession = Depends(get_db_session),
    repository: RecipientRepository = Depends(get_repository)
) -> Recipient:
    recipient = await repository.get(recipient_id, session)
    return Recipient.model_validate(recipient)


@router.put('/{recipient_id}')
async def update(
    recipient_id: t.Annotated[int, Path()],
    name: t.Annotated[str, Body()],
    lastname: t.Annotated[str, Body()],
    age: t.Annotated[int, Body()],
    contact_email: t.Annotated[EmailStr, Body()],
    session: AsyncSession = Depends(get_db_session),
    repository: RecipientRepository = Depends(get_repository)
) -> Recipient:
    updated_recipient = await repository.update(recipient_id, name, lastname, age, contact_email, session)
    return Recipient.model_validate(updated_recipient)


@router.delete('/{recipient_id}', status_code=204)
async def delete(
    recipient_id: int,
    session: AsyncSession = Depends(get_db_session),
    repository: RecipientRepository = Depends(get_repository)
) -> None:
    await repository.delete(recipient_id, session)
