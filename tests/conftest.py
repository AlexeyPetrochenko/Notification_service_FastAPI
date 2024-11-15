import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime, timedelta
from pydantic import EmailStr
from unittest.mock import patch

from app.config import load_from_env_for_tests
from app.db import BaseOrm
from app.repository.campaign import CampaignRepository
from app.repository.recipient import RecipientRepository
from app.models import StatusCampaign, CampaignOrm, StatusNotification, NotificationOrm, RecipientOrm
from app.server import create_app


# TODO: В тестах не должно быть глобальных переменных заменить их на фикстуры
test_config = load_from_env_for_tests()
engine_test = create_async_engine(url=test_config.ASYNC_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=engine_test, expire_on_commit=False)
BaseOrm.bind = engine_test


@pytest.fixture
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(BaseOrm.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(BaseOrm.metadata.drop_all) 


@pytest.fixture
async def test_session():
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
def campaign_repository():
    return CampaignRepository()
    

@pytest.fixture
def recipient_repository():
    return RecipientRepository()
    

@pytest.fixture
def make_campaign(faker, minute_in_future):
    def inner(
        name: str = None, 
        content: str = None,
        launch_date: datetime | str | None = None
    ):
        return {
            'name': name or faker.catch_phrase(), 
            'content': content or faker.text(max_nb_chars=100), 
            'launch_date': launch_date or minute_in_future
        }   
    return inner


@pytest.fixture
def make_recipient(faker):
    def inner(
        name: str = None,
        lastname: str = None,
        age: int = None,
        contact_email: EmailStr = None
    ):
        return {
            'name': name or faker.first_name(),
            'lastname': lastname or faker.last_name(),
            'age': age or faker.random_int(min=14, max=90),
            'contact_email': contact_email or faker.email()
        }
    return inner


@pytest.fixture
def make_campaign_orm(faker, minute_in_future):
    def inner(
        campaign_id: int = None,
        name: str = None,
        content: str = None,
        status: StatusCampaign = None,
        launch_date: datetime = None,
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        return CampaignOrm(
            campaign_id=campaign_id or faker.random_int(1, 1000),
            name=name or faker.catch_phrase(),
            content=content or faker.text(100),
            status=status or StatusCampaign.CREATED,
            launch_date=launch_date or minute_in_future, 
            created_at=created_at or datetime.now(),
            updated_at=updated_at or datetime.now()
        )
    return inner


@pytest.fixture
def make_campaign_entity(faker, minute_in_future, test_session):
    async def inner(
        name: str = None, 
        content: str = None, 
        launch_date: datetime = None, 
        status: StatusCampaign = None
    ):
        new_campaign = CampaignOrm(
            name=name or faker.catch_phrase(), 
            content=content or faker.text(100), 
            status=status or StatusCampaign.CREATED, 
            launch_date=launch_date or minute_in_future,
        )
        test_session.add(new_campaign)
        await test_session.commit()
        return new_campaign
    return inner


@pytest.fixture
def make_recipient_entities(make_recipient, test_session):
    async def inner(count: int) -> list[RecipientOrm]:
        recipients = [RecipientOrm(**make_recipient()) for _ in range(count)]
        test_session.add_all(recipients)
        await test_session.commit()
        
        return recipients
    return inner


@pytest.fixture
def make_notification_entities(test_session):
    async def inner(status: StatusNotification, campaign_id: int, recipients: list[RecipientOrm]) -> list[NotificationOrm]:
        notifications = []
        for recipient in recipients:
            notifications.append(
                NotificationOrm(
                    status=status,
                    campaign_id=campaign_id,
                    recipient_id=recipient.recipient_id
                )
            )
        test_session.add_all(notifications)
        await test_session.commit()
        return notifications
    return inner
            

@pytest.fixture
def minute_in_past():
    return datetime.now() - timedelta(minutes=1)
        

@pytest.fixture
def minute_in_future():
    return datetime.now() + timedelta(minutes=1)


@pytest.fixture
def random_id(faker):
    return faker.random_int(min=1, max=10000)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url='http://test') as ac:
        yield ac


@pytest.fixture
def campaign_repo_add_mock(make_campaign_orm):
    with patch('app.routers.campaign.CampaignRepository.add') as mock:
        mock.return_value = make_campaign_orm()
        yield mock
        

@pytest.fixture
def campaign_repo_get_all_mock():
    with patch('app.routers.campaign.CampaignRepository.get_all') as mock:
        yield mock


@pytest.fixture
def campaign_repo_get_mock(make_campaign_orm):
    with patch('app.routers.campaign.CampaignRepository.get') as mock:
        mock.return_value = make_campaign_orm()
        yield mock
        
        
@pytest.fixture
def campaign_repo_update_mock(make_campaign_orm):
    with patch('app.routers.campaign.CampaignRepository.update') as mock:
        mock.return_value = make_campaign_orm()
        yield mock
        
        
@pytest.fixture
def campaign_repo_delete_mock():
    with patch('app.routers.campaign.CampaignRepository.delete') as mock:
        yield mock
        
        
@pytest.fixture
def campaign_repo_run_mock():
    with patch('app.routers.campaign.CampaignRepository.run') as mock:
        yield mock
        
        
@pytest.fixture
def campaign_repo_acquire_mock(make_campaign_orm):
    with patch('app.routers.campaign.CampaignRepository.acquire') as mock:
        mock.return_value = make_campaign_orm() 
        yield mock


@pytest.fixture
def campaign_repo_complete_mock():
    with patch('app.routers.campaign.CampaignRepository.complete') as mock:
        yield mock
