"""API request/response schemas.

The rich Pydantic domain models in :mod:`app.models` double as response
schemas. This package holds the few *request-only* shapes that differ from
the persisted models (e.g. creating a project by name only).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class NameUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


__all__ = ["ProjectCreate", "NameUpdate"]
