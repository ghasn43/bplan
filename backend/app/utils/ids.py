"""ID and timestamp helpers shared across models and services."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone


def new_id() -> str:
    """Return a short, URL-safe unique identifier."""
    return uuid.uuid4().hex


def utcnow() -> datetime:
    """Timezone-aware UTC timestamp used for created_at / updated_at."""
    return datetime.now(timezone.utc)
