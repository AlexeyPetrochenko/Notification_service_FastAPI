from sqlalchemy import select
import pytest
from fastapi import HTTPException

from app.models import RecipientOrm


async def test__create_recipient__entry_created_successfully(prepare_database, recipient_repository, test_session):
    new_recipient = await recipient_repository.create_recipient(
        name='Firstname',
        lastname='Lastname',
        age=34,
        contact_email='test@fake.com'
    )
    
    query = select(RecipientOrm).where(RecipientOrm.recipient_id == new_recipient.recipient_id)
    result = await test_session.execute(query)
    recipient = result.scalars().first()
    
    assert recipient is not None
    

async def test__create_recipient__all_fields_created(prepare_database, recipient_repository, test_session):
    data = {'name': 'Firstname', 'lastname': 'Lastname', 'age': 34, 'contact_email': 'test@fake.com'}
    
    new_recipient = await recipient_repository.create_recipient(**data)
    query = select(RecipientOrm).where(RecipientOrm.recipient_id == new_recipient.recipient_id)
    result = await test_session.execute(query)
    recipient = result.scalars().first()
    
    assert recipient.name == data['name']
    assert recipient.lastname == data['lastname']
    assert recipient.age == data['age']
    assert recipient.contact_email == data['contact_email']


async def test__create_recipient__exception_when_field_contact_email_with_taken(prepare_database, recipient_repository):
    data = {'name': 'Firstname', 'lastname': 'Lastname', 'age': 34, 'contact_email': 'test@fake.com'}
    await recipient_repository.create_recipient(**data)
    
    with pytest.raises(HTTPException):
        await recipient_repository.create_recipient(**data)
