"""Schemas for the Excel financial model export."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ExcelExportRequest(BaseModel):
    scenario: str = "base"                       # base | conservative | optimistic | all
    projection_detail: str = "annual"           # monthly | annual | both  (v1 builds annual)
    workbook_type: str = "editable"             # editable | presentation | full
    include_assumptions: bool = True
    include_schedules: bool = True
    include_statements: bool = True
    include_ratios: bool = True
    include_scenarios: bool = True
    include_charts: bool = True
    include_checks: bool = True
    include_text_summary: bool = False
    protect_formulas: bool = True


class ExcelExportFile(BaseModel):
    export_id: str
    project_id: str
    file_name: str
    file_size: int = 0
    scenario: str
    status: str = "ready"                        # ready | failed
    generated_at: datetime
    warnings: list[str] = Field(default_factory=list)
    message: str | None = None


class ExcelExportResponse(ExcelExportFile):
    download_url: str


class ExcelExportPreview(BaseModel):
    project_id: str
    company_name: str
    project_name: str
    currency: str
    period_range: str
    scenario: str
    scenario_label: str
    sheets: list[str] = Field(default_factory=list)
    protect_formulas: bool = True
    data_ready: bool = True
    can_generate: bool = True
    blocking: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    estimated_size_kb: int = 0
