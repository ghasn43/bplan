"""Pydantic schemas for the IFRS-style Statement of Profit or Loss."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------
# Periods
# --------------------------------------------------------------------------
class IncomeStatementPeriod(BaseModel):
    index: int
    label: str                      # "Jan 2026" or "Year 1"
    period_type: str                # "month" | "year"
    year_index: int                 # 0-based projection year
    month: int | None = None        # 1-12 for monthly view
    year: int
    start_date: date
    end_date: date


# --------------------------------------------------------------------------
# Line items / sections
# --------------------------------------------------------------------------
class IncomeStatementLineItem(BaseModel):
    key: str
    label: str
    classification: str
    values_by_period: list[float] = Field(default_factory=list)
    total: float = 0.0
    is_subtotal: bool = False
    is_grand_total: bool = False
    display_order: int = 0
    drilldown_available: bool = False
    note: str | None = None
    children: list["IncomeStatementLineItem"] = Field(default_factory=list)


class IncomeStatementSection(BaseModel):
    key: str
    title: str
    display_order: int = 0
    line_items: list[IncomeStatementLineItem] = Field(default_factory=list)
    subtotal: IncomeStatementLineItem | None = None


# --------------------------------------------------------------------------
# Totals / margins / warnings / metadata
# --------------------------------------------------------------------------
class IncomeStatementTotals(BaseModel):
    total_revenue: float = 0.0
    total_cost_of_sales: float = 0.0
    gross_profit: float = 0.0
    total_other_income: float = 0.0
    total_operating_expenses: float = 0.0
    operating_profit: float = 0.0
    ebitda: float = 0.0
    total_finance_costs: float = 0.0
    profit_before_tax: float = 0.0
    income_tax_expense: float = 0.0
    profit_for_period: float = 0.0


class IncomeStatementMargins(BaseModel):
    gross_margin_pct: list[float] = Field(default_factory=list)
    ebitda: list[float] = Field(default_factory=list)
    ebitda_margin_pct: list[float] = Field(default_factory=list)
    operating_margin_pct: list[float] = Field(default_factory=list)
    net_margin_pct: list[float] = Field(default_factory=list)
    # totals (whole-period)
    gross_margin_total_pct: float = 0.0
    ebitda_margin_total_pct: float = 0.0
    operating_margin_total_pct: float = 0.0
    net_margin_total_pct: float = 0.0


class IncomeStatementWarning(BaseModel):
    code: str
    severity: str                   # info | warning | critical
    message: str


class IncomeStatementMetadata(BaseModel):
    project_id: str
    project_name: str
    scenario: str
    scenario_label: str
    view: str                       # monthly | yearly
    currency: str
    statement_title: str = "Statement of Profit or Loss"
    period_caption: str
    generated_at: datetime


class IncomeStatementResponse(BaseModel):
    metadata: IncomeStatementMetadata
    periods: list[IncomeStatementPeriod]
    sections: list[IncomeStatementSection]
    totals: IncomeStatementTotals
    margins: IncomeStatementMargins
    analytical: list[IncomeStatementLineItem] = Field(default_factory=list)
    warnings: list[IncomeStatementWarning] = Field(default_factory=list)


class IncomeStatementSummary(BaseModel):
    project_id: str
    scenario: str
    currency: str
    total_revenue: float
    gross_profit: float
    ebitda: float
    operating_profit: float
    profit_before_tax: float
    net_profit: float
    gross_margin: float
    ebitda_margin: float
    net_profit_margin: float


class ReconciliationCheck(BaseModel):
    key: str
    label: str
    passed: bool
    severity: str                   # info | warning | critical
    detail: str | None = None


class IncomeStatementReconciliation(BaseModel):
    project_id: str
    scenario: str
    all_passed: bool
    checks: list[ReconciliationCheck] = Field(default_factory=list)
    warnings: list[IncomeStatementWarning] = Field(default_factory=list)


IncomeStatementLineItem.model_rebuild()
