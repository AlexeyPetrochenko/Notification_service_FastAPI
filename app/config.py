from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    
    APP_URL: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_NAME: str
    EMAIL_PASS: str
    
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXP: int
    
    TOKEN_WORKER: str
    
    RMQ_USER: str
    RMQ_PASS: str
    RMQ_HOST: str
    RMQ_PORT: int
    
    model_config = SettingsConfigDict(env_file='.env', extra="ignore")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    @property 
    def RABBIT_MQ_URL(self) -> str:
        return f'pyamqp://{self.RMQ_USER}:{self.RMQ_PASS}@{self.RMQ_HOST}:{self.RMQ_PORT}/'


class TestConfig(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXP: int
    
    model_config = SettingsConfigDict(env_prefix="TEST_", env_file=".env", extra="ignore")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


def load_from_env() -> Config:
    return Config()  # type: ignore


def load_from_env_for_tests() -> Config:
    return TestConfig()  # type: ignore
