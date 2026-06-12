"""Schemas for the IFRS Statement of Cash Flows (indirect method)."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class CashFlowPeriod(BaseModel):
    index: int
    label: str
    period_type: str                 # monthly | annual
    start_date: date
    end_date: date


class CashFlowLineItem(BaseModel):
    key: str
    label: str
    classification: str              # operating | investing | financing | summary
    level: int = 1
    values_by_period: list[float] = Field(default_factory=list)
    total: float = 0.0
    is_section_header: bool = False
    is_subtotal: bool = False
    is_grand_total: bool = False
    drilldown_available: bool = False
    note: str | None = None
    children: list["CashFlowLineItem"] = Field(default_factory=list)


class CashFlowTotals(BaseModel):
    net_cash_from_operating_activities: list[float] = Field(default_factory=list)
    net_cash_used_in_investing_activities: list[float] = Field(default_factory=list)
    net_cash_from_financing_activities: list[float] = Field(default_factory=list)
    net_change_in_cash: list[float] = Field(default_factory=list)
    opening_cash: list[float] = Field(default_factory=list)
    closing_cash: list[float] = Field(default_factory=list)


class CashReconciliationResult(BaseModel):
    closing_cash_cash_flow: list[float] = Field(default_factory=list)
    cash_balance_sheet: list[float] = Field(default_factory=list)
    difference: list[float] = Field(default_factory=list)
    max_difference: float = 0.0
    status: str = "reconciled"        # reconciled | not_reconciled


class CashFlowWarning(BaseModel):
    code: str
    severity: str                    # info | warning | critical
    message: str


class CashFlowMetadata(BaseModel):
    project_id: str
    project_name: str
    scenario: str
    scenario_label: str
    view: str
    method: str = "indirect"
    currency: str
    statement_title: str = "Statement of Cash Flows"
    period_caption: str
    generated_at: datetime


class CashFlowResponse(BaseModel):
    metadata: CashFlowMetadata
    periods: list[CashFlowPeriod] = Field(default_factory=list)
    rows: list[CashFlowLineItem] = Field(default_factory=list)
    totals: CashFlowTotals = Field(default_factory=CashFlowTotals)
    cash_reconciliation: CashReconciliationResult = Field(default_factory=CashReconciliationResult)
    warnings: list[CashFlowWarning] = Field(default_factory=list)


class CashFlowSummary(BaseModel):
    project_id: str
    scenario: str
    currency: str
    net_operating_cash_flow: float
    net_investing_cash_flow: float
    net_financing_cash_flow: float
    net_change_in_cash: float
    closing_cash: float
    free_cash_flow: float
    reconciliation_status: str


class ReconciliationCheck(BaseModel):
    key: str
    label: str
    passed: bool
    severity: str
    detail: str | None = None


class CashFlowReconciliation(BaseModel):
    project_id: str
    scenario: str
    all_passed: bool
    checks: list[ReconciliationCheck] = Field(default_factory=list)
    warnings: list[CashFlowWarning] = Field(default_factory=list)


CashFlowLineItem.model_rebuild()
