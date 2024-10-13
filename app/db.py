from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


async_engine = create_async_engine(url=settings.ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=async_engine)


class BaseOrm(DeclarativeBase):
    pass
