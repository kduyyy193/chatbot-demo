from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    RELOAD: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
