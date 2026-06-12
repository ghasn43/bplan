"""Aggregate BusinessPlanProject model + completion/review value objects."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from .base import TimestampedModel
from .capital import Financing, WorkingCapitalAssumption
from .catalog import DirectCostItem, ProductService, RevenueAssumption
from .compliance import TaxAssumption
from .costs import FixedAsset, OperatingExpense, StartupCost
from .identity import ProjectSetup
from .people import StaffRole
from .planning import KPIAssumption, ScenarioAssumption
from .projection import ProjectionData
from .text_plan import TextPlanDocument


class BusinessPlanProject(TimestampedModel):
    """Root aggregate holding every assumption section for one plan.

    The whole document is persisted as a single JSON record today; the same
    shape maps cleanly onto a future relational schema (one table per list).
    """

    name: str = Field(..., min_length=1, max_length=200)

    setup: ProjectSetup | None = None
    products: list[ProductService] = Field(default_factory=list)
    revenue: list[RevenueAssumption] = Field(default_factory=list)
    direct_costs: list[DirectCostItem] = Field(default_factory=list)
    staffing: list[StaffRole] = Field(default_factory=list)
    operating_expenses: list[OperatingExpense] = Field(default_factory=list)
    startup_costs: list[StartupCost] = Field(default_factory=list)
    fixed_assets: list[FixedAsset] = Field(default_factory=list)
    working_capital: WorkingCapitalAssumption | None = None
    financing: Financing = Field(default_factory=Financing)
    tax: TaxAssumption | None = None
    scenarios: list[ScenarioAssumption] = Field(default_factory=list)
    kpis: KPIAssumption | None = None

    # Two-layer architecture: per-item monthly projection schedules.
    # The income statement reads these as the source of truth.
    projections: ProjectionData = Field(default_factory=ProjectionData)

    # Written (textual) business plan: sections -> topics -> rich text + images.
    text_plan: TextPlanDocument = Field(default_factory=TextPlanDocument)


class ProjectSummary(BaseModel):
    """Lightweight projection-list item (avoids shipping the full document)."""

    id: str
    name: str
    business_name: str | None = None
    currency: str | None = None
    projection_period: str | None = None
    completion_percent: int = 0
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------------
# Completion / review value objects (Pages 14)
# --------------------------------------------------------------------------
class SectionStatus(BaseModel):
    key: str
    label: str
    complete: bool
    required: bool
    item_count: int | None = None
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CompletionReport(BaseModel):
    project_id: str
    completion_percent: int
    completed_sections: int
    total_sections: int
    sections: list[SectionStatus]


class ReviewStatus(BaseModel):
    """Full review payload backing Page 14."""

    project_id: str
    completion: CompletionReport
    ready_for_projection: bool
    blocking_issues: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
