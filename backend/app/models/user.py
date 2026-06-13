"""User + audit-log domain models for authentication and access control."""
from __future__ import annotations

from datetime import datetime

from pydantic import Field

from .base import TimestampedModel

# role: admin | user


class User(TimestampedModel):
    email: str = Field(..., min_length=3, max_length=200)
    username: str | None = Field(default=None, max_length=80)
    full_name: str = Field(default="", max_length=200)
    password_hash: str = ""
    role: str = "user"                       # admin | user
    company_id: str | None = None            # required for user, null for admin
    is_active: bool = True
    is_verified: bool = False
    must_change_password: bool = False
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    last_login_at: datetime | None = None
    created_by_user_id: str | None = None
    notes: str | None = Field(default=None, max_length=2000)


class AuditLog(TimestampedModel):
    user_id: str | None = None
    action: str = ""
    entity_type: str | None = None
    entity_id: str | None = None
    company_id: str | None = None
    project_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    details: str | None = None
