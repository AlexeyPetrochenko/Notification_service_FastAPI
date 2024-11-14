from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import typing as t

from app.models import RecipientOrm
from app.exceptions import ConflictException, NotFoundException


class RecipientRepository:
    async def add(
        self, name: str, lastname: str, age: int, contact_email: EmailStr, session: AsyncSession
    ) -> RecipientOrm:
        recipient = RecipientOrm(name=name, lastname=lastname, age=age, contact_email=contact_email)
        session.add(recipient)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ConflictException(f'A recipient with this [email: {contact_email}] already exists')
        return recipient

    async def get_all(self, session: AsyncSession) -> t.Sequence[RecipientOrm]:
        query = select(RecipientOrm)
        result = await session.execute(query)
        recipients = result.scalars().all()
        return recipients

    async def get(self, recipient_id: int, session: AsyncSession) -> RecipientOrm:
        recipient = await session.get(RecipientOrm, recipient_id)
        if recipient is None:
            raise NotFoundException(f'Recipient [recipient_id: {recipient_id}] not found')
        return recipient

    async def update(
        self, recipient_id: int, name: str, lastname: str, age: int, contact_email: EmailStr, session: AsyncSession
    ) -> RecipientOrm:
        recipient = await session.get(RecipientOrm, recipient_id)
        if recipient is None:
            raise NotFoundException(f'Recipient [recipient_id: {recipient_id}] not found')
        recipient.name = name
        recipient.lastname = lastname
        recipient.age = age
        recipient.contact_email = contact_email
        
        session.add(recipient)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise ConflictException(f'A recipient with this [email: {contact_email}] already exists')
        return recipient

    async def delete(self, recipient_id: int, session: AsyncSession) -> None:
        recipient = await session.get(RecipientOrm, recipient_id)
        if recipient is None:
            raise NotFoundException(f'Recipient [recipient_id: {recipient_id}] not found')
        await session.delete(recipient)
        await session.commit()
