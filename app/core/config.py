from __future__ import annotations

import json
from functools import lru_cache
from typing import Annotated, Any, Self

from pydantic import AliasChoices, Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def _normalize_origin(origin: str) -> str:
    normalized = origin.strip()
    if normalized != "*":
        normalized = normalized.rstrip("/")
    return normalized


class Settings(BaseSettings):
    app_name: str = "Gestor de Despensa API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_debug: bool = True
    api_v1_prefix: str = "/api"
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: DEFAULT_CORS_ORIGINS.copy()
    )
    frontend_base_url: str = "http://localhost:5173"
    database_url: str = Field(validation_alias=AliasChoices("DATABASE_URL", "DATABASE_PUBLIC_URL"))
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expires_in_minutes: int = 2880
    google_client_id: str
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash-lite"
    gemini_fallback_model: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def normalize_cors_origins(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value

        raw_value = value.strip()
        if not raw_value:
            return []

        if raw_value.startswith("["):
            try:
                value = json.loads(raw_value)
                if isinstance(value, list):
                    return value
            except json.JSONDecodeError:
                pass

        return [_normalize_origin(origin) for origin in raw_value.split(",") if origin.strip()]

    @model_validator(mode="after")
    def include_frontend_base_url_in_cors(self) -> Self:
        cors_origins = []
        for origin in self.cors_origins:
            normalized_origin = _normalize_origin(origin)
            if normalized_origin and normalized_origin not in cors_origins:
                cors_origins.append(normalized_origin)

        frontend_origin = _normalize_origin(self.frontend_base_url)
        if frontend_origin and frontend_origin not in cors_origins:
            cors_origins.append(frontend_origin)

        self.cors_origins = cors_origins
        return self

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        if value.startswith("postgresql+psycopg://"):
            return value
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
