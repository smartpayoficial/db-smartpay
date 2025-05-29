from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    TITLE: str = Field(..., env="WEP_APP_TITLE")
    VERSION: str = Field(..., env="WEB_APP_VERSION")
    DESCRIPTION: str = Field(..., env="WEP_APP_DESCRIPTION")
    ENVIRONMENT: str = Field(...)

    POSTGRES_DATABASE_URL: str = Field(...)
    DEFAULT_DATA: bool = Field(...)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
