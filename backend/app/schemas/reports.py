"""Schemas for the business plan report generator."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    scenario: str = "base"
    view: str = "yearly"
    report_style: str = "investor"            # investor | bank | board | management | full
    include_charts: bool = True
    include_appendices: bool = True
    include_assumptions: bool = True
    include_warnings: bool = True
    output_format: str = "docx"               # docx | pdf

    # Textual business plan (written narrative) options.
    include_text_plan: bool = True
    text_plan_include_completed: bool = True
    text_plan_include_drafts: bool = True
    text_plan_include_images: bool = True
    text_plan_include_guidance: bool = False


class ReportWarning(BaseModel):
    code: str
    severity: str                             # info | warning | critical
    message: str


class ReportSection(BaseModel):
    key: str
    title: str
    available: bool = True


class ReportFile(BaseModel):
    report_id: str
    file_name: str
    format: str                               # docx | pdf | html
    scenario: str
    view: str
    report_style: str
    status: str = "ready"                     # ready | failed
    size_bytes: int = 0
    created_at: datetime
    message: str | None = None


class ReportResponse(BaseModel):
    report_id: str
    file_name: str
    format: str
    scenario: str
    view: str
    report_style: str
    status: str
    size_bytes: int
    created_at: datetime
    download_url: str
    message: str | None = None


class ReportPreview(BaseModel):
    project_id: str
    title: str
    company: str
    project_name: str | None = None
    scenario: str
    scenario_label: str
    view: str
    currency: str
    period_range: str
    prepared_date: str
    prepared_for: str
    sections: list[ReportSection] = Field(default_factory=list)
    completion_percent: int = 0
    data_ready: bool = True
    can_generate: bool = True
    blocking: list[str] = Field(default_factory=list)
    warnings: list[ReportWarning] = Field(default_factory=list)
    highlights: list[dict] = Field(default_factory=list)


class ReportGenerationStatus(BaseModel):
    stage: str
    progress: int = 0
    message: str | None = None
