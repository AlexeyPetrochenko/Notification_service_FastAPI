import pytest

from app.models import RecipientOrm
from app.exceptions import ConflictException


async def test__add__entry_created_successfully(prepare_database, recipient_repository, test_session, make_recipient):  # noqa: U100
    new_recipient = await recipient_repository.add(**make_recipient(), session=test_session)
    
    recipient = await test_session.get(RecipientOrm, new_recipient.recipient_id)
    
    assert recipient is not None
    
    
async def test__add__all_fields_success_created(prepare_database, test_session, recipient_repository, make_recipient):  # noqa: U100
    data = make_recipient()
    recipient = await recipient_repository.add(**data, session=test_session)    

    assert recipient.name == data['name']
    assert recipient.lastname == data['lastname']
    assert recipient.age == data['age']
    assert recipient.contact_email == data['contact_email']
    

async def test__add__exception_when_field_contact_email_with_taken(prepare_database, recipient_repository, make_recipient, test_session):  # noqa: U100
    data = make_recipient(contact_email='taken@example.com')
    await recipient_repository.add(**data, session=test_session)
    
    with pytest.raises(ConflictException):
        await recipient_repository.add(**data, session=test_session)
