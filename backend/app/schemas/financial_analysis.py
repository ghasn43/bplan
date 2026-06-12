"""Schemas for the Financial Analysis (charts & KPI) dashboard.

The backend returns chart-ready data so the frontend only renders — it never
re-computes financial figures.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FinancialAnalysisPeriod(BaseModel):
    index: int
    label: str
    period_type: str


class ChartSeries(BaseModel):
    key: str
    label: str
    format: str = "currency"          # currency | percent | ratio | number
    color: str | None = None
    type: str | None = None           # for combo charts: "bar" | "line"
    axis: str = "left"                # left | right


class FinancialAnalysisChart(BaseModel):
    key: str
    title: str
    description: str | None = None
    chart_type: str                   # line | bar | grouped_bar | stacked_bar | donut | pie | area | waterfall | combo
    unit: str = "currency"
    data: list[dict[str, Any]] = Field(default_factory=list)
    series: list[ChartSeries] = Field(default_factory=list)
    source_statement: str = "Projected financial statements"
    insight: str | None = None
    warnings: list[str] = Field(default_factory=list)


class FinancialAnalysisSection(BaseModel):
    key: str
    title: str
    description: str | None = None
    charts: list[FinancialAnalysisChart] = Field(default_factory=list)


class FinancialAnalysisKPI(BaseModel):
    key: str
    label: str
    value: float | None = None
    format: str = "currency"          # currency | percent | ratio | number
    group: str                        # profitability | liquidity | leverage | efficiency | cash
    hint: str | None = None
    good: bool | None = None          # True = healthy, False = concerning, None = neutral


class FinancialAnalysisWarning(BaseModel):
    code: str
    severity: str                     # info | warning | critical
    message: str


class FinancialAnalysisMetadata(BaseModel):
    project_id: str
    project_name: str
    scenario: str
    scenario_label: str
    view: str
    currency: str
    generated_at: datetime


class FinancialAnalysisResponse(BaseModel):
    metadata: FinancialAnalysisMetadata
    periods: list[FinancialAnalysisPeriod] = Field(default_factory=list)
    kpis: list[FinancialAnalysisKPI] = Field(default_factory=list)
    sections: list[FinancialAnalysisSection] = Field(default_factory=list)
    insights: list[str] = Field(default_factory=list)
    warnings: list[FinancialAnalysisWarning] = Field(default_factory=list)


class ScenarioSeries(BaseModel):
    scenario: str
    label: str
    values: list[float] = Field(default_factory=list)


class ScenarioMetric(BaseModel):
    key: str
    label: str
    format: str = "currency"
    series: list[ScenarioSeries] = Field(default_factory=list)


class ScenarioComparisonResponse(BaseModel):
    project_id: str
    project_name: str
    view: str
    currency: str
    periods: list[str] = Field(default_factory=list)
    metrics: list[ScenarioMetric] = Field(default_factory=list)
    generated_at: datetime
