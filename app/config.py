import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()


@dataclass
class Settings:
    DB_USER: Optional[str]
    DB_PASS: Optional[str]
    DB_HOST: Optional[str]
    DB_PORT: Optional[str]
    DB_NAME: Optional[str]

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f'postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    

settings = Settings(
    DB_USER=os.getenv('DB_USER'),
    DB_PASS=os.getenv('DB_PASS'),
    DB_HOST=os.getenv('DB_HOST'),
    DB_PORT=os.getenv('DB_PORT'),
    DB_NAME=os.getenv('DB_NAME')
)

test_settings = Settings(
    os.getenv('TEST_DB_USER'),
    os.getenv('TEST_DB_PASS'),
    os.getenv('TEST_DB_HOST'),
    os.getenv('TEST_DB_PORT'),
    os.getenv('TEST_DB_NAME')
)
