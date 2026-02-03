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

    CELERY_RETRY_BACKOFF_MAX: int = Field(60)
    CELERY_MAX_RETRIES: int = Field(3)
    REDIS_URL: str = Field("redis://localhost:6380/0")

    HTTP_TIMEOUT: float = Field(30.0)

    METEOGRAM_BASE_URL: str = Field(...)
    METEOGRAM_BASE_PATH: str = Field("tmp/meteograms")

    ETL_SCHEDULE_HOUR: int = Field(6)
    ETL_SCHEDULE_MINUTE: int = Field(0)

    MIN_FILE_SIZE_BYTES: int = Field(100)


settings = Settings()
