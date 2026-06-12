"""Page 1 — Project Setup model."""
from __future__ import annotations

from datetime import date

from pydantic import Field, field_validator

from .base import EntityBase
from .enums import (
    BusinessModel,
    ProjectionFrequency,
    ProjectionPeriod,
    ReportingStandard,
)


class ProjectSetup(EntityBase):
    """Basic identity and projection structure of the business plan."""

    business_name: str = Field(..., min_length=1, max_length=200)
    project_name: str | None = Field(default=None, max_length=200)
    business_description: str | None = Field(default=None, max_length=4000)
    industry: str | None = Field(default=None, max_length=120)
    business_model: BusinessModel | None = None
    country: str | None = Field(default=None, max_length=120)
    city: str | None = Field(default=None, max_length=120)

    # Currency is selected once here and reused across the whole app.
    currency: str = Field(..., min_length=3, max_length=3, description="ISO 4217 code")

    projection_start_date: date
    projection_period: ProjectionPeriod
    projection_frequency: ProjectionFrequency = ProjectionFrequency.MONTHLY

    tax_jurisdiction: str | None = Field(default=None, max_length=120)
    reporting_standard: ReportingStandard = ReportingStandard.MANAGEMENT
    scenario_mode_enabled: bool = False

    @field_validator("currency")
    @classmethod
    def _upper_currency(cls, v: str) -> str:
        return v.upper()
