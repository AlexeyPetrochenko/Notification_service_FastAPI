from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import load_from_env


config = load_from_env()
async_engine = create_async_engine(url=config.ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(bind=async_engine, expire_on_commit=False)


class BaseOrm(DeclarativeBase):
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'
