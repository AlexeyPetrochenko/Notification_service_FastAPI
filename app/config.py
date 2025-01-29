from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    
    APP_URL: str
    EMAIL_HOST: str
    EMAIL_PORT: str
    EMAIL_NAME: str
    EMAIL_PASS: str
    
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXP: int
    
    model_config = SettingsConfigDict(env_file='.env', extra="ignore")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


class TestConfig(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    
    model_config = SettingsConfigDict(env_prefix="TEST_", env_file=".env", extra="ignore")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


def load_from_env() -> Config:
    return Config()  # type: ignore


def load_from_env_for_tests() -> Config:
    return TestConfig()  # type: ignore
