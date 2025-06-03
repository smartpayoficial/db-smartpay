from pydantic import BaseSettings


class Settings(BaseSettings):
    # App Settings
    DEBUGGER: bool = False
    WEB_APP_VERSION: str = "0.1.0"
    WEP_APP_TITLE: str = "smartpay-db"
    WEP_APP_DESCRIPTION: str = "Database service for SmartPay"
    ENVIRONMENT: str = "dev"

    # Database Settings
    POSTGRES_DATABASE_URL: str
    DEFAULT_DATA: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
