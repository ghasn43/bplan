"""Schemas for the projection period engine and the editable projection grids."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ProjectionPeriod(BaseModel):
    id: str
    period_index: int
    period_label: str
    period_type: str                 # "monthly" | "annual"
    start_date: date
    end_date: date
    fiscal_year: int
    projection_year: int             # 1-based
    month_number: int | None = None
    quarter_number: int | None = None


# -- Grid cell / row / grid -------------------------------------------------
class GridCell(BaseModel):
    period_index: int
    # editable inputs (subset depending on section; extras simply omitted)
    quantity: float | None = None
    amount: float | None = None
    price_override: float | None = None
    discount_override: float | None = None
    refund_override: float | None = None
    quantity_driver: float | None = None
    amount_override: float | None = None
    percentage_override: float | None = None
    manual_cost_amount: float | None = None
    active: bool = True
    notes: str | None = None
    # computed (read-only) outputs
    value: float = 0.0               # net revenue / final cost / final expense
    gross: float | None = None
    discount_amount: float | None = None
    refund_amount: float | None = None


class GridRow(BaseModel):
    item_id: str
    label: str
    group: str | None = None
    note: str | None = None
    cells: list[GridCell] = Field(default_factory=list)
    total: float = 0.0


class ProjectionGrid(BaseModel):
    project_id: str
    section: str                     # revenue | direct_costs | operating_expenses
    mode: str                        # monthly | annual
    currency: str
    periods: list[ProjectionPeriod] = Field(default_factory=list)
    rows: list[GridRow] = Field(default_factory=list)
    totals_by_period: list[float] = Field(default_factory=list)
    grand_total: float = 0.0
    warnings: list[str] = Field(default_factory=list)


# -- Mutation payloads ------------------------------------------------------
class CellPatch(BaseModel):
    item_id: str
    period_index: int
    quantity: float | None = None
    amount: float | None = None
    price_override: float | None = None
    discount_override: float | None = None
    refund_override: float | None = None
    quantity_driver: float | None = None
    amount_override: float | None = None
    percentage_override: float | None = None
    manual_cost_amount: float | None = None
    active: bool | None = None
    notes: str | None = None
    clear_overrides: bool = False


class BulkPatch(BaseModel):
    mode: str = "monthly"
    cells: list[CellPatch] = Field(default_factory=list)


class ApplyGrowthRequest(BaseModel):
    mode: str = "monthly"
    item_id: str | None = None       # None = apply to all rows
    base_value: float | None = None  # None = use first active period value
    growth_percent: float = 0.0      # per-period growth (monthly or annual per mode)
    start_index: int = 0


class FillRightRequest(BaseModel):
    mode: str = "monthly"
    item_id: str
    from_index: int = 0
