import pytest
from sqlalchemy.exc import IntegrityError

from app.models import UserOrm


async def test__add__success_added_new_user(prepare_database, user_repository, test_session):  # noqa: U100
    email: str = 'test_email@test.ru'
    hash_password: str = 'hash_password'
    
    user = await user_repository.add(test_session, email=email, hash_password=hash_password)
    user_in_db = await test_session.get(UserOrm, user.user_id)
    
    assert user_in_db.email == email


async def test__add__exception__on_duplicate_email(prepare_database, user_repository, test_session):  # noqa: U100
    email: str = 'test_email@test.ru'
    hash_password: str = 'hash_password'
    
    await user_repository.add(test_session, email=email, hash_password=hash_password)
    with pytest.raises(IntegrityError):
        await user_repository.add(test_session, email=email, hash_password=hash_password)
    

async def test__get__successful_return_of_campaign_by_id(
    prepare_database, make_object_user, test_session, user_repository  # noqa: U100
):
    user = await make_object_user(email='test_email@test.ru', hash_password='hash_password')
    
    user_in_db = await user_repository.get(test_session, user_id=user.user_id)
    
    assert user_in_db.email == user.email


async def test__get_by_email__successful_return_of_campaign_by_email(
    prepare_database, make_object_user, test_session, user_repository  # noqa: U100
):
    user = await make_object_user(email='test_email@test.ru', hash_password='hash_password')
    
    user_in_db = await user_repository.get_by_email(test_session, email='test_email@test.ru')
    
    assert user_in_db.user_id == user.user_id
