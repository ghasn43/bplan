"""Schemas for the fixed-asset depreciation schedule and summary."""
from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class DepreciationPeriod(BaseModel):
    index: int
    label: str
    period_type: str            # monthly | annual
    start_date: date
    end_date: date


class DepreciationAssetRow(BaseModel):
    asset_id: str
    label: str
    category: str
    category_label: str
    depreciation_by_period: list[float] = Field(default_factory=list)
    total_depreciation: float = 0.0
    closing_net_book_value: float = 0.0


class DepreciationRollforward(BaseModel):
    """Aggregate fixed-asset roll-forward by period."""

    opening_cost: list[float] = Field(default_factory=list)
    additions: list[float] = Field(default_factory=list)
    depreciation_charge: list[float] = Field(default_factory=list)
    accumulated_depreciation: list[float] = Field(default_factory=list)
    closing_net_book_value: list[float] = Field(default_factory=list)


class DepreciationSchedule(BaseModel):
    project_id: str
    view: str
    currency: str
    periods: list[DepreciationPeriod] = Field(default_factory=list)
    assets: list[DepreciationAssetRow] = Field(default_factory=list)
    rollforward: DepreciationRollforward = Field(default_factory=DepreciationRollforward)
    totals_by_period: list[float] = Field(default_factory=list)
    grand_total_depreciation: float = 0.0
    total_closing_nbv: float = 0.0
    warnings: list[str] = Field(default_factory=list)


class FixedAssetSummary(BaseModel):
    project_id: str
    currency: str
    total_asset_cost: float
    annual_depreciation: float
    net_book_value: float
    active_assets: int
    loan_financed_assets: int
    software_intangible_assets: int
    total_assets: int
