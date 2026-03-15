"""Configuração centralizada via Pydantic Settings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    ENVIRONMENT: str = Field("development")
    REDIS_URL: str = Field("redis://localhost:6379/0")


    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection URL (ex: postgresql://cempa:...@localhost:5432/sigedam)",
    )

    HTTP_TIMEOUT: float = Field(30.0)
    MAX_RETRIES: int = Field(3)
    RETRY_BACKOFF_MAX: int = Field(60)

    SMTP_HOST: str = Field("smtp.gmail.com")
    SMTP_PORT: int = Field(587)
    SMTP_EMAIL: str = Field("")
    SMTP_PASSWORD: str = Field("")

    WHATSAPP_INSTANCE: str = Field("")
    WHATSAPP_TOKEN: str = Field("")
    WHATSAPP_CLIENT_TOKEN: str = Field("")

    FRONTEND_URL: str = Field("", description="URL para links de gerenciamento nos templates")


settings = Settings()
