"""Schemas for the IFRS Statement of Financial Position (Balance Sheet)."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class BalanceSheetPeriod(BaseModel):
    index: int
    label: str                       # "Dec 2026" or "Year 1"
    period_type: str                 # monthly | annual
    as_at_date: date


class BalanceSheetLineItem(BaseModel):
    key: str
    label: str
    classification: str              # asset | liability | equity | check
    level: int = 1                   # 0 = section header, 1 = line, 2 = sub-line
    values_by_period: list[float] = Field(default_factory=list)
    is_header: bool = False
    is_subtotal: bool = False
    is_grand_total: bool = False
    is_balance_check: bool = False
    drilldown_available: bool = False
    note: str | None = None
    children: list["BalanceSheetLineItem"] = Field(default_factory=list)


class BalanceSheetSection(BaseModel):
    key: str
    label: str
    line_items: list[BalanceSheetLineItem] = Field(default_factory=list)


class BalanceCheckResult(BaseModel):
    values_by_period: list[float] = Field(default_factory=list)      # assets - (E + L)
    is_balanced_by_period: list[bool] = Field(default_factory=list)
    max_difference: float = 0.0
    status: str = "balanced"                                          # balanced | out_of_balance


class BalanceSheetTotals(BaseModel):
    total_non_current_assets: list[float] = Field(default_factory=list)
    total_current_assets: list[float] = Field(default_factory=list)
    total_assets: list[float] = Field(default_factory=list)
    total_equity: list[float] = Field(default_factory=list)
    total_non_current_liabilities: list[float] = Field(default_factory=list)
    total_current_liabilities: list[float] = Field(default_factory=list)
    total_liabilities: list[float] = Field(default_factory=list)
    total_equity_and_liabilities: list[float] = Field(default_factory=list)


class BalanceSheetWarning(BaseModel):
    code: str
    severity: str                    # info | warning | critical
    message: str


class BalanceSheetMetadata(BaseModel):
    project_id: str
    project_name: str
    scenario: str
    scenario_label: str
    view: str
    currency: str
    statement_title: str = "Statement of Financial Position"
    as_at_caption: str
    generated_at: datetime


class BalanceSheetResponse(BaseModel):
    metadata: BalanceSheetMetadata
    periods: list[BalanceSheetPeriod] = Field(default_factory=list)
    rows: list[BalanceSheetLineItem] = Field(default_factory=list)
    totals: BalanceSheetTotals = Field(default_factory=BalanceSheetTotals)
    balance_check: BalanceCheckResult = Field(default_factory=BalanceCheckResult)
    warnings: list[BalanceSheetWarning] = Field(default_factory=list)


class BalanceSheetSummary(BaseModel):
    project_id: str
    scenario: str
    currency: str
    total_assets: float
    cash: float
    net_working_capital: float
    total_borrowings: float
    total_equity: float
    inventory: float
    receivables: float
    payables: float
    current_ratio: float | None = None
    debt_to_equity: float | None = None
    balance_status: str


class ReconciliationCheck(BaseModel):
    key: str
    label: str
    passed: bool
    severity: str
    detail: str | None = None


class BalanceSheetReconciliation(BaseModel):
    project_id: str
    scenario: str
    all_passed: bool
    checks: list[ReconciliationCheck] = Field(default_factory=list)
    warnings: list[BalanceSheetWarning] = Field(default_factory=list)


class OpeningBalanceSheet(BaseModel):
    """Placeholder for a future opening-balance-sheet input (not required yet)."""

    cash: float = 0.0
    receivables: float = 0.0
    inventory: float = 0.0
    prepayments: float = 0.0
    fixed_assets_net: float = 0.0
    payables: float = 0.0
    borrowings: float = 0.0
    tax_payable: float = 0.0
    vat_payable: float = 0.0
    share_capital: float = 0.0
    retained_earnings: float = 0.0


BalanceSheetLineItem.model_rebuild()
