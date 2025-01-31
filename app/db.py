from typing import Callable, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import load_from_env, Config


def get_engine(config: Config = Depends(load_from_env)) -> AsyncEngine:
    return create_async_engine(url=config.ASYNC_DATABASE_URL)
    
    
def get_session_maker(engine: AsyncEngine = Depends(get_engine)) -> Callable[[], AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db_session(db: Callable[[], AsyncSession] = Depends(get_session_maker)) -> AsyncGenerator:
    async with db() as session:
        yield session


class BaseOrm(DeclarativeBase):
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}>'
