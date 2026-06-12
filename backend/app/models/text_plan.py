"""Textual business plan domain models (persisted inside the project document).

The written plan is a tree: Document -> Sections -> Topics -> (rich text + images).
It is stored on :class:`BusinessPlanProject.text_plan` so it serialises with the
rest of the project (single JSON record today, one-table-per-list tomorrow).
"""
from __future__ import annotations

from pydantic import Field

from .base import TimestampedModel

# Open string vocabularies (kept as plain str so the user can add custom values).
# section_type:  executive_summary | company_overview | market_analysis |
#                products_services | business_model | operations_plan |
#                marketing_sales | management_team | risk_analysis |
#                financial_plan | funding_request | implementation_plan |
#                appendix | custom
# topic_type:    paragraph | image_text | table | checklist | quote | callout | custom
# status:        not_started | draft | in_review | completed
# alignment:     left | center | right | full_width


class TextPlanImage(TimestampedModel):
    file_name: str = ""
    original_file_name: str = ""
    file_path: str = ""              # path relative to the uploads root
    url: str = ""                    # API URL the frontend/report can load
    mime_type: str = ""
    file_size: int = 0
    width: int | None = None
    height: int | None = None
    caption: str = ""
    alt_text: str = ""
    alignment: str = "center"
    display_width_percentage: int = 100
    order_index: int = 0


class TextPlanTopic(TimestampedModel):
    section_id: str | None = None
    title: str = "Untitled topic"
    content_html: str = ""
    content_json: dict | None = None
    plain_text: str = ""
    order_index: int = 0
    topic_type: str = "paragraph"
    include_in_report: bool = True
    status: str = "not_started"
    priority: str = "normal"         # low | normal | high
    word_count: int = 0
    reading_time_minutes: float = 0.0
    guidance_text: str = ""
    images: list[TextPlanImage] = Field(default_factory=list)
    formatting_metadata: dict = Field(default_factory=dict)


class TextPlanSection(TimestampedModel):
    title: str = "Untitled section"
    subtitle: str = ""
    description: str = ""
    section_type: str = "custom"
    order_index: int = 0
    collapsed: bool = False
    include_in_report: bool = True
    page_break_before: bool = True
    status: str = "not_started"
    guidance_text: str = ""
    topics: list[TextPlanTopic] = Field(default_factory=list)


class TextPlanDocument(TimestampedModel):
    title: str = "Written Business Plan"
    template_id: str | None = None
    business_type: str | None = None
    sections: list[TextPlanSection] = Field(default_factory=list)
