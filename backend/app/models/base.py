"""Shared base models providing identity and audit timestamps."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from ..utils.ids import new_id, utcnow


class TimestampedModel(BaseModel):
    """Base for any persisted record: stable id + audit timestamps."""

    model_config = ConfigDict(populate_by_name=True, validate_assignment=True)

    id: str = Field(default_factory=new_id)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    def touch(self) -> None:
        """Update the modification timestamp (called on every write)."""
        self.updated_at = utcnow()


class EntityBase(TimestampedModel):
    """Base for user-editable line items that carry free-text notes."""

    notes: str | None = Field(default=None, max_length=2000)
