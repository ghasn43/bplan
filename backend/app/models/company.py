"""Company entity — the parent of one or more business plan projects."""
from __future__ import annotations

from pydantic import Field

from .base import TimestampedModel

# status: active | inactive | demo


class Company(TimestampedModel):
    """A company/legal entity. Projects reference it via ``company_id``."""

    company_name: str = Field(..., min_length=1, max_length=200)
    trading_name: str | None = Field(default=None, max_length=200)
    legal_name: str | None = Field(default=None, max_length=200)
    industry_sector: str | None = Field(default=None, max_length=160)
    business_description: str | None = Field(default=None, max_length=4000)
    country: str | None = Field(default=None, max_length=120)
    city: str | None = Field(default=None, max_length=120)
    website: str | None = Field(default=None, max_length=300)
    logo_path: str | None = None
    status: str = "active"
    notes: str | None = Field(default=None, max_length=2000)


class CompanySummary(TimestampedModel):
    """Company list item with aggregated, clearly-labelled project totals."""

    company_name: str
    industry_sector: str | None = None
    country: str | None = None
    city: str | None = None
    business_description: str | None = None
    status: str = "active"
    total_projects: int = 0
    active_projects: int = 0
    draft_projects: int = 0
    profile_completion_percent: int = 0
