from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/aex_rag"
    ANTHROPIC_API_KEY: str = ""
    VOYAGE_API_KEY: str = ""
    NMS_BASE_URL: str = ""
    ZMS_BASE_URL: str = ""
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
