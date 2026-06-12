"""Projection-schedule storage (the two-layer architecture).

Each financial item (revenue stream, direct cost item, operating expense item)
has a *setup* (the existing master-data models) and a *projection schedule*
stored here. The schedule is the income statement's source of truth.

Schedules are stored at **monthly** granularity (one cell per month for the
whole projection horizon). The annual view is always derived by aggregation, and
annual-mode edits are spread back across the relevant months. Schedules are
seeded deterministically from the setup defaults + growth/inflation helpers, then
become user-editable and authoritative once persisted.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class RevenueCell(BaseModel):
    quantity: float = 0.0
    price_override: float | None = None
    discount_override: float | None = None     # percent
    refund_override: float | None = None        # percent
    active: bool = True
    notes: str | None = None


class DirectCostCell(BaseModel):
    quantity_driver: float | None = None        # optional manual unit driver
    amount_override: float | None = None         # per-unit amount override
    percentage_override: float | None = None     # percent override
    manual_cost_amount: float | None = None      # overrides the whole computed cost
    active: bool = True
    notes: str | None = None


class OpexCell(BaseModel):
    amount: float = 0.0
    amount_override: float | None = None
    active: bool = True
    notes: str | None = None


class ProjectionData(BaseModel):
    """All projection schedules for a project, keyed by item id (monthly cells)."""

    revenue: dict[str, list[RevenueCell]] = Field(default_factory=dict)
    direct_costs: dict[str, list[DirectCostCell]] = Field(default_factory=dict)
    operating_expenses: dict[str, list[OpexCell]] = Field(default_factory=dict)
