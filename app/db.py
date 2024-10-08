from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import ASYNC_DATABASE_URL


async_engine = create_async_engine(url=ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=async_engine)


class BaseOrm(DeclarativeBase):
    pass


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseOrm.metadata.create_all)


async def delete_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseOrm.metadata.drop_all)
