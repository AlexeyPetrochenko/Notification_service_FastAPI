import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime, timedelta
import faker
import random
from pydantic import EmailStr


from app.config import load_from_env_for_tests
from app.db import BaseOrm
from app.repository.campaign import CampaignRepository
from app.repository.recipient import RecipientRepository
from app.models import StatusCampaign, CampaignOrm
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
async def get_faker():
    return faker.Faker()


@pytest.fixture
async def campaign_repository():
    yield CampaignRepository()
    

@pytest.fixture
async def recipient_repository():
    yield RecipientRepository()
    

@pytest.fixture
async def make_campaign(get_faker):
    def function_make_campaign(
        name: str = None, 
        content: str = None,
        launch_date: datetime | str | None = None
    ):
        
        return {
            'name': name if name else get_faker.catch_phrase(), 
            'content': content if content else get_faker.text(max_nb_chars=100), 
            'launch_date': launch_date if launch_date else get_faker.date_time_between(start_date='now', end_date='+30d')
        }   
    return function_make_campaign


@pytest.fixture
async def make_recipient(get_faker):
    def inner(
        name: str = None,
        lastname: str = None,
        age: int = None,
        contact_email: EmailStr = None
    ):
        return {
            'name': name or get_faker.first_name(),
            'lastname': lastname or get_faker.last_name(),
            'age': age or get_faker.random_int(min=14, max=90),
            'contact_email': contact_email or get_faker.email()
        }
    return inner


@pytest.fixture
async def make_campaign_orm(get_faker):
    def function_make_campaign_orm(
        campaign_id: int = random.randint(1, 100),
        name: str = get_faker.catch_phrase(),
        content: str = get_faker.text(100),
        status: StatusCampaign = StatusCampaign.CREATED,
        launch_date: datetime = get_faker.date_time_between(start_date='now', end_date='+30d'),
        created_at: datetime = get_faker.date_time_between(start_date='now', end_date='+30d'),
        updated_at: datetime = get_faker.date_time_between(start_date='now', end_date='+30d'),
    ):
        return CampaignOrm(
            campaign_id=campaign_id,
            name=name,
            content=content,
            status=status,
            launch_date=launch_date, 
            created_at=created_at,
            updated_at=updated_at
        )
    return function_make_campaign_orm


@pytest.fixture
async def make_campaign_entity():
    async def function_make_campaign_entity(name: str, content: str, launch_date: datetime, status: StatusCampaign = StatusCampaign.CREATED):
        async with TestSessionLocal() as session:
            new_campaign = CampaignOrm(name=name, content=content, status=status, launch_date=launch_date)
            session.add(new_campaign)
            await session.commit()
            return new_campaign
    return function_make_campaign_entity


@pytest.fixture
async def minute_in_past():
    return datetime.now() - timedelta(minutes=1)
        

@pytest.fixture
async def minute_in_future():
    return datetime.now() + timedelta(minutes=1)


@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=create_app()), base_url='http://test') as ac:
        yield ac
