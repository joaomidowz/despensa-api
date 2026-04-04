from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Gestor de Despensa API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True
    api_v1_prefix: str = "/api"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    frontend_base_url: str = "http://localhost:5173"
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expires_in_minutes: int = 2880
    google_client_id: str
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash-lite"
    gemini_fallback_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
