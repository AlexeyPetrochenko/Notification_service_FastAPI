import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class Config:
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    APP_URL: str

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f'postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    

def load_from_env() -> Config:
    return Config(
        DB_USER=os.environ['DB_USER'],
        DB_PASS=os.environ['DB_PASS'],
        DB_HOST=os.environ['DB_HOST'],
        DB_PORT=os.environ['DB_PORT'],
        DB_NAME=os.environ['DB_NAME'],
        APP_URL=os.environ['APP_URL']
    )
# TODO @alex: для тестов тоже сделать функцию


def load_from_env_for_tests() -> Config:
    return Config(
        DB_USER=os.environ['TEST_DB_USER'],
        DB_PASS=os.environ['TEST_DB_PASS'],
        DB_HOST=os.environ['TEST_DB_HOST'],
        DB_PORT=os.environ['TEST_DB_PORT'],
        DB_NAME=os.environ['TEST_DB_NAME'],
        APP_URL=os.environ['APP_URL']
    )
