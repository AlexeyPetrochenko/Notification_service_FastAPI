from fastapi import Depends
import typing as t
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import load_from_env, Config


def get_config() -> Config:
    return load_from_env()


def get_engine(config: Config = Depends(get_config)) -> AsyncEngine:
    return create_async_engine(url=config.ASYNC_DATABASE_URL)
    
    
def get_db(engine: AsyncEngine = Depends(get_engine)) -> t.Callable[[], AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db_session(db: t.Callable[[], AsyncSession] = Depends(get_db)) -> t.AsyncGenerator:
    async with db() as session:
        yield session


class BaseOrm(DeclarativeBase):
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'
