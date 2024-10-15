from fastapi import APIRouter, Body, Path
from pydantic import EmailStr
import typing as t

from app.schemas import Recipient
from app.db import AsyncSessionLocal
from app.repository.recipient import RecipientRepository


router = APIRouter(prefix='/recipients')
recipient_repository = RecipientRepository(AsyncSessionLocal)


@router.post('/', status_code=201)
async def add(
    name: t.Annotated[str, Body(examples=['Julia'])],
    lastname: t.Annotated[str, Body(examples=['Roberts'])],
    age: t.Annotated[int, Body(examples=[56], lt=100)],
    contact_email: t.Annotated[EmailStr, Body(examples=['julia@example.com'])]
) -> Recipient:
    recipient = await recipient_repository.create_recipient(name, lastname, age, contact_email)
    return Recipient.model_validate(recipient)


@router.get('/')
async def get_all() -> list[Recipient]:
    recipients = await recipient_repository.get_all_recipients()
    return [Recipient.model_validate(recipient) for recipient in recipients]


@router.get('/{recipient_id}')
async def get(recipient_id: int) -> Recipient:
    recipient = await recipient_repository.get_recipient(recipient_id)
    return Recipient.model_validate(recipient)


@router.put('/{recipient_id}')
async def update(
    recipient_id: t.Annotated[int, Path()],
    name: t.Annotated[str, Body()],
    lastname: t.Annotated[str, Body()],
    age: t.Annotated[int, Body()],
    contact_email: t.Annotated[EmailStr, Body()]
) -> Recipient:
    updated_recipient = await recipient_repository.update_recipient(recipient_id, name, lastname, age, contact_email)
    return Recipient.model_validate(updated_recipient)


@router.delete('/{recipient_id}', status_code=204)
async def delete(recipient_id: int) -> None:
    await recipient_repository.delete_recipient(recipient_id)
