import logging
import pytest
from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictException, CredentialsException


logger = logging.getLogger(__name__)


async def test__register_user__mock_is_called_once(user_repository_add_mock, user_service, test_session, make_user_orm):
    user_repository_add_mock.return_value = make_user_orm
    
    await user_service.register_user(session=test_session, email='test_email@test.ru', password='test_password')
    
    assert user_repository_add_mock.call_count == 1


async def test__register_user__raises_conflict_exception_on_integrity_error(user_repository_add_mock, user_service, test_session):
    user_repository_add_mock.side_effect = IntegrityError(None, None, None)
    
    with pytest.raises(ConflictException):
        await user_service.register_user(session=test_session, email='test_email@test.ru', password='test_password')


async def test__authenticate_user__credentials_exception_when_user_by_email_is_not_found(
    user_repository_get_by_email_mock, test_session, auth_service
):
    user_repository_get_by_email_mock.side_effect = CredentialsException()
    
    with pytest.raises(CredentialsException):
        await auth_service.authenticate_user(session=test_session, email='test_email@test.ru', password='test_password')


async def test__authenticate_user__credentials_exception_when_password_not_verified(
    user_repository_get_by_email_mock, verify_password_mock, test_session, auth_service, make_user_orm
):
    user_repository_get_by_email_mock.return_value = make_user_orm
    verify_password_mock.return_value = False
    
    with pytest.raises(CredentialsException):
        await auth_service.authenticate_user(session=test_session, email='test_email@test.ru', password='test_password')


async def test__authenticate_user__mock_is_called_once(
    user_repository_get_by_email_mock, verify_password_mock, test_session, auth_service, make_user_orm
): 
    user_repository_get_by_email_mock.return_value = make_user_orm
    verify_password_mock.return_value = True
    
    await auth_service.authenticate_user(session=test_session, email='test_email@test.ru', password='test_password')
    
    assert user_repository_get_by_email_mock.call_count == 1
    assert verify_password_mock.call_count == 1
