import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Enterprise settings management loaded securely from environment variables / .env file.
    """
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # JWT Security Settings
    JWT_SECRET_KEY: str = Field(
        default="marketpulse_enterprise_super_secret_key_change_in_production_9876543210",
        description="Secret key for signing JWT tokens"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database Settings (PostgreSQL default, SQLite fallback)
    DATABASE_URL: str = Field(
        default="sqlite:///./marketpulse.db",
        description="Database connection string"
    )

    # Redis Settings (Caching & Celery Queue)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant Settings (Vector Intelligence)
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""

    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
