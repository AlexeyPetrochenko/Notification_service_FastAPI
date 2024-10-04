from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import SYNC_DATABASE_URL, ASYNC_DATABASE_URL


sync_engine = create_engine(url=SYNC_DATABASE_URL, echo=False)
async_engine = create_async_engine(url=ASYNC_DATABASE_URL)

SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False) 
AsyncSessionLocal = async_sessionmaker(bind=async_engine)


class BaseOrm(DeclarativeBase):
    pass


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseOrm.metadata.create_all)


async def delete_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseOrm.metadata.drop_all)
