import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictException


async def test__register_user__mock_is_called_once(user_repository_add_mock, user_service, test_session, make_user_orm):
    user_repository_add_mock.return_value = make_user_orm
    
    await user_service.register_user(session=test_session, email='test_email@test.ru', password='test_password')
    
    assert user_repository_add_mock.call_count == 1


async def test__register_user__raises_conflict_exception_on_integrity_error(user_repository_add_mock, user_service, test_session):
    user_repository_add_mock.side_effect = IntegrityError(None, None, None)
    
    with pytest.raises(ConflictException):
        await user_service.register_user(session=test_session, email='test_email@test.ru', password='test_password')
