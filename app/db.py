from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from .config import SYNC_DATABASE_URL


sync_engine = create_engine(url=SYNC_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False) 


class BaseOrm(DeclarativeBase):
    pass
