import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.config import TEST_ASYNC_DATABASE_URL
from app.db import BaseOrm
from app.repository import CampaignRepository


engine_test = create_async_engine(url=TEST_ASYNC_DATABASE_URL, poolclass=NullPool)
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
    




# @pytest.fixture
# async def async_client():
#     async with AsyncClient(app=app, base_url='http://test') as ac:
#         yield ac
