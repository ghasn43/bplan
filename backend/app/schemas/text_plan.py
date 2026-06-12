"""Request/response DTOs for the textual business plan API."""
from __future__ import annotations

from pydantic import BaseModel, Field

from ..models.text_plan import TextPlanDocument, TextPlanSection, TextPlanTopic


# --------------------------------------------------------------------------
# section / topic create + update payloads (all fields optional on update)
# --------------------------------------------------------------------------
class SectionCreate(BaseModel):
    title: str = "Untitled section"
    subtitle: str = ""
    description: str = ""
    section_type: str = "custom"
    guidance_text: str = ""
    include_in_report: bool = True
    page_break_before: bool = True
    order_index: int | None = None


class SectionUpdate(BaseModel):
    title: str | None = None
    subtitle: str | None = None
    description: str | None = None
    section_type: str | None = None
    guidance_text: str | None = None
    collapsed: bool | None = None
    include_in_report: bool | None = None
    page_break_before: bool | None = None
    status: str | None = None


class TopicCreate(BaseModel):
    section_id: str
    title: str = "Untitled topic"
    content_html: str = ""
    topic_type: str = "paragraph"
    guidance_text: str = ""
    include_in_report: bool = True
    order_index: int | None = None


class TopicUpdate(BaseModel):
    title: str | None = None
    content_html: str | None = None
    content_json: dict | None = None
    topic_type: str | None = None
    guidance_text: str | None = None
    include_in_report: bool | None = None
    status: str | None = None
    priority: str | None = None


class ImageUpdate(BaseModel):
    caption: str | None = None
    alt_text: str | None = None
    alignment: str | None = None
    display_width_percentage: int | None = None
    order_index: int | None = None


# --------------------------------------------------------------------------
# reorder / move
# --------------------------------------------------------------------------
class ReorderSectionsRequest(BaseModel):
    ordered_section_ids: list[str] = Field(default_factory=list)


class ReorderTopicsRequest(BaseModel):
    section_id: str
    ordered_topic_ids: list[str] = Field(default_factory=list)


class MoveTopicRequest(BaseModel):
    topic_id: str
    target_section_id: str
    target_order_index: int = 0


# --------------------------------------------------------------------------
# outline templates + suggestions
# --------------------------------------------------------------------------
class TemplateTopicInfo(BaseModel):
    title: str
    topic_type: str = "paragraph"
    guidance_text: str = ""


class TemplateSectionInfo(BaseModel):
    title: str
    section_type: str = "custom"
    description: str = ""
    guidance_text: str = ""
    topics: list[TemplateTopicInfo] = Field(default_factory=list)


class OutlineTemplateInfo(BaseModel):
    id: str
    name: str
    description: str = ""
    business_types: list[str] = Field(default_factory=list)
    section_count: int = 0
    topic_count: int = 0
    sections: list[TemplateSectionInfo] = Field(default_factory=list)


class OutlineSuggestionResponse(BaseModel):
    detected_business_type: str
    recommended_template_id: str
    explanation: str
    report_style: str | None = None
    templates: list[OutlineTemplateInfo] = Field(default_factory=list)


class ApplyOutlineTemplateRequest(BaseModel):
    template_id: str
    mode: str = "replace"                          # replace | append
    selected_section_titles: list[str] | None = None   # None = all sections
    selected_topic_titles: list[str] | None = None     # None = all topics
    with_sample_content: bool = False


# --------------------------------------------------------------------------
# completion + preview
# --------------------------------------------------------------------------
class TextPlanCompletion(BaseModel):
    project_id: str
    completion_percent: int = 0
    section_count: int = 0
    topic_count: int = 0
    completed_topics: int = 0
    draft_topics: int = 0
    empty_topics: int = 0
    word_count: int = 0
    image_count: int = 0
    sections_in_report: int = 0
    topics_in_report: int = 0
    missing_key_sections: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class TextPlanPreviewTopic(BaseModel):
    id: str
    title: str
    content_html: str
    status: str
    word_count: int
    include_in_report: bool
    image_count: int


class TextPlanPreviewSection(BaseModel):
    id: str
    title: str
    description: str
    include_in_report: bool
    status: str
    topics: list[TextPlanPreviewTopic] = Field(default_factory=list)


class TextPlanPreview(BaseModel):
    project_id: str
    title: str
    section_count: int
    topic_count: int
    sections: list[TextPlanPreviewSection] = Field(default_factory=list)


# Re-export the persisted document so routes can return the full tree.
__all__ = [
    "TextPlanDocument",
    "TextPlanSection",
    "TextPlanTopic",
    "SectionCreate",
    "SectionUpdate",
    "TopicCreate",
    "TopicUpdate",
    "ImageUpdate",
    "ReorderSectionsRequest",
    "ReorderTopicsRequest",
    "MoveTopicRequest",
    "OutlineTemplateInfo",
    "OutlineSuggestionResponse",
    "ApplyOutlineTemplateRequest",
    "TemplateSectionInfo",
    "TemplateTopicInfo",
    "TextPlanCompletion",
    "TextPlanPreview",
]
