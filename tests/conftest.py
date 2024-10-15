import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from datetime import datetime

from app.config import test_settings
from app.db import BaseOrm
from app.repository.campaign import CampaignRepository
from app.repository.recipient import RecipientRepository
from app.models import StatusCampaign, CampaignOrm
from main import app


engine_test = create_async_engine(url=test_settings.ASYNC_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=engine_test)
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
async def campaign_repository():
    yield CampaignRepository(TestSessionLocal)
    

@pytest.fixture
async def recipient_repository():
    yield RecipientRepository(TestSessionLocal)
    

@pytest.fixture
async def campaign_data_factory():
    def function_create_data(
        name: str = 'Black Friday', 
        content: str = 'Discounts up to 50%', 
        status: StatusCampaign = StatusCampaign.CREATED, 
        launch_date: datetime | str = datetime(2024, 11, 1, 12, 0, 0)
    ):
        return {
            'name': name, 
            'content': content, 
            'status': status, 
            'launch_date': launch_date
        }   
    return function_create_data


@pytest.fixture
async def make_campaign():
    async def function_make_campaign(name: str, content: str, status: StatusCampaign, launch_date: datetime):
        async with TestSessionLocal() as session:
            new_campaign = CampaignOrm(name=name, content=content, status=status, launch_date=launch_date)
            session.add(new_campaign)
            await session.commit()
            await session.refresh(new_campaign)
            return new_campaign
    return function_make_campaign
    

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test/campaigns') as ac:
        yield ac
