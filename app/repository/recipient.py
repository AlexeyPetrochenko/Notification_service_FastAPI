from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from dataclasses import dataclass
import typing as t

from app.models import RecipientOrm


@dataclass
class RecipientRepository:
    session_maker: t.Callable[[], AsyncSession]
    
    async def create_recipient(self, name: str, lastname: str, age: int, contact_email: EmailStr) -> RecipientOrm:
        async with self.session_maker() as session: 
            recipient = RecipientOrm(name=name, lastname=lastname, age=age, contact_email=contact_email)
            session.add(recipient)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=400, detail='A recipient with this email already exists')
            await session.refresh(recipient)
            return recipient

    async def get_all_recipients(self) -> t.Sequence[RecipientOrm]:
        async with self.session_maker() as session:
            query = select(RecipientOrm)
            result = await session.execute(query)
            recipients = result.scalars().all()
            return recipients

    async def get_recipient(self, recipient_id: int) -> RecipientOrm:
        async with self.session_maker() as session:
            query = select(RecipientOrm).where(RecipientOrm.recipient_id == recipient_id)
            result = await session.execute(query)
            recipient = result.scalars().first()
            if recipient is None:
                raise HTTPException(status_code=404, detail='Recipient not found')
            return recipient

    async def update_recipient(self, recipient_id: int, name: str, lastname: str, age: int, contact_email: EmailStr) -> RecipientOrm:
        async with self.session_maker() as session:
            query = select(RecipientOrm).where(RecipientOrm.recipient_id == recipient_id)
            result = await session.execute(query)
            recipient = result.scalars().first()
            if recipient is None:
                raise HTTPException(status_code=404, detail='Recipient not found')
            recipient.name = name
            recipient.lastname = lastname
            recipient.age = age
            recipient.contact_email = contact_email
            
            session.add(recipient)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                raise HTTPException(status_code=400, detail='A recipient with this email already exists')
            await session.refresh(recipient)
            return recipient

    async def delete_recipient(self, recipient_id: int) -> None:
        async with self.session_maker() as session:
            query = select(RecipientOrm).where(RecipientOrm.recipient_id == recipient_id)
            result = await session.execute(query)
            recipient = result.scalars().first()
            if recipient is None:
                raise HTTPException(status_code=404, detail='A recipient with this email already exists')
            await session.delete(recipient)
            await session.commit()
