from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AcervoHub"
    environment: str = "development"
    secret_key: str = Field(default="dev-only-secret-change-me")
    access_token_expire_minutes: int = 120
    password_hash_rounds: int = 12
    database_url: str = "sqlite:///./acervo_hub.db"
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    seed_database: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
