import pytest
from fastapi import HTTPException

from app.models import RecipientOrm


async def test__add__entry_created_successfully(prepare_database, recipient_repository, test_session, make_recipient):  # noqa: U100
    new_recipient = await recipient_repository.add(**make_recipient(), session=test_session)
    
    recipient = await test_session.get(RecipientOrm, new_recipient.recipient_id)
    
    assert recipient is not None
    
    
async def test__add_returns_value_recipient_orm(prepare_database, test_session, recipient_repository, make_recipient):  # noqa: U100
    recipient = await recipient_repository.add(**make_recipient(), session=test_session)    

    assert isinstance(recipient, RecipientOrm)
    

async def test__add__exception_when_field_contact_email_with_taken(prepare_database, recipient_repository, make_recipient, test_session):  # noqa: U100
    data = make_recipient(contact_email='taken@example.com')
    await recipient_repository.add(**data, session=test_session)
    
    with pytest.raises(HTTPException):
        await recipient_repository.add(**data, session=test_session)
