import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime
import faker
import random

from app.config import load_from_env_for_tests
from app.db import BaseOrm
from app.repository.campaign import CampaignRepository
from app.repository.recipient import RecipientRepository
from app.workers.campaign_worker import CampaignWorker
from app.models import StatusCampaign, CampaignOrm
from main import app


test_config = load_from_env_for_tests()
engine_test = create_async_engine(url=test_config.ASYNC_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=engine_test)
BaseOrm.bind = engine_test
fake = faker.Faker()


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
async def campaign_repository():
    yield CampaignRepository(TestSessionLocal)
    

@pytest.fixture
async def recipient_repository():
    yield RecipientRepository(TestSessionLocal)
    

@pytest.fixture
async def make_campaign():
    def function_make_campaign(
        name: str = None, 
        content: str = None,
        launch_date: datetime | str | None = None
    ):
        
        return {
            'name': name if name else fake.catch_phrase(), 
            'content': content if content else fake.text(max_nb_chars=100), 
            'launch_date': launch_date if launch_date else fake.date_time_between(start_date='now', end_date='+30d')
        }   
    return function_make_campaign


@pytest.fixture
async def make_campaign_orm():
    def function_make_campaign_orm(
        campaign_id: int = random.randint(1, 100),
        name: str = fake.catch_phrase(),
        content: str = fake.text(100),
        status: StatusCampaign = StatusCampaign.CREATED,
        launch_date: datetime = fake.date_time_between(start_date='now', end_date='+30d'),
        created_at: datetime = fake.date_time_between(start_date='now', end_date='+30d'),
        updated_at: datetime = fake.date_time_between(start_date='now', end_date='+30d'),
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
            await session.refresh(new_campaign)
            return new_campaign
    return function_make_campaign_entity
    

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as ac:
        yield ac


@pytest.fixture
async def campaign_worker():
    yield CampaignWorker(TestSessionLocal, AsyncClient)
