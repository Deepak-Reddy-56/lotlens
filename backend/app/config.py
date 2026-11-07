from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


class Settings:
    app_name: str = os.getenv("APP_NAME", "LotLens API")
    app_env: str = os.getenv("APP_ENV", "development")
    database_url: str = os.getenv(
        "DATABASE_URL", "sqlite+aiosqlite:///./lotlens.db"
    )
    hindsight_api_key: str | None = os.getenv("HINDSIGHT_API_KEY")
    hindsight_base_url: str = os.getenv(
        "HINDSIGHT_BASE_URL", "https://api.hindsight.vectorize.io"
    )
    hindsight_bank_id: str = os.getenv("HINDSIGHT_BANK_ID", "lotlens-dev")
    cors_origins: list[str] = [
        item.strip()
        for item in os.getenv(
            "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
        ).split(",")
        if item.strip()
    ]


settings = Settings()
