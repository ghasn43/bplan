"""Application configuration.

Centralises runtime settings so the storage backend can later be swapped
from JSON files to PostgreSQL without touching the rest of the codebase.
"""
from __future__ import annotations

import os
from pathlib import Path


class Settings:
    """Lightweight settings object (env-driven, no external deps)."""

    app_name: str = "Business Plan Projection API"
    api_prefix: str = "/api"

    # Storage --------------------------------------------------------------
    # "json" today; "postgres" is the planned upgrade path. The service layer
    # depends only on the StorageBackend interface, so swapping this value
    # (plus providing a PostgresStorage implementation) is the only change
    # required to migrate persistence.
    storage_backend: str = os.getenv("BP_STORAGE_BACKEND", "json")
    data_dir: Path = Path(os.getenv("BP_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))

    # CORS -----------------------------------------------------------------
    cors_origins: list[str] = os.getenv(
        "BP_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")

    # Seed a demo project on first boot if the store is empty.
    seed_on_startup: bool = os.getenv("BP_SEED_ON_STARTUP", "true").lower() == "true"


settings = Settings()
