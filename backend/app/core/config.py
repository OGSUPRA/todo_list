from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Todo Product API"
    environment: str = "production"
    secret_key: str = Field(..., min_length=32)
    database_url: str = "postgresql+psycopg://todo:todo@postgres:5432/todo"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:8081"]
    media_root: str = str(BASE_DIR / "media")
    refresh_cookie_name: str = "todo_refresh_token"
    secure_cookies: bool = False
    admin_emails: list[str] = ["admin@example.com"]
    auth_rate_limit: str = "20/minute"
    write_rate_limit: str = "80/minute"
    read_rate_limit: str = "240/minute"
    metrics_enabled: bool = False
    grafana_url: str = "http://localhost:3000"
    prometheus_url: str = "http://localhost:9090"
    loki_url: str = "http://localhost:3100"
    pgadmin_url: str = "http://localhost:5050"


settings = Settings()
