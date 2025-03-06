from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8000
    RELOAD: bool = True
    ENVIRONMENT: str = "development"
    TELEGRAM_BOT_TOKEN: str = "TELEGRAM_BOT_TOKEN"
    WEBHOOK_URL: str  = "WEBHOOK_URL"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
