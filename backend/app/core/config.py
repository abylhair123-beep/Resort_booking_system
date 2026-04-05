from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Uyaly_Booking API"
    app_version: str = "1.0.0"
    debug: bool = False

    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/uyaly_booking"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
