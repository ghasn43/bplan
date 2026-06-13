"""Textual business plan service: CRUD + reorder + completion + preview.

All mutations follow the project read-modify-write pattern: load the aggregate
from storage, mutate ``project.text_plan``, persist, and return the result.
"""
from __future__ import annotations

import html as _html
import re

from ..models import BusinessPlanProject
from ..models.text_plan import (
    TextPlanDocument,
    TextPlanSection,
    TextPlanTopic,
)
from ..storage.base import NotFoundError, StorageBackend
from ..utils.ids import utcnow

KEY_SECTION_TYPES = {
    "executive_summary",
    "company_overview",
    "market_analysis",
    "financial_plan",
}


class TextPlanError(Exception):
    """Invalid text-plan operation (mapped to HTTP 400/404)."""


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html or "")
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    return re.sub(r"\s+", " ", text).strip()


def _recompute_topic_metrics(topic: TextPlanTopic) -> None:
    topic.plain_text = _strip_html(topic.content_html)
    words = len(topic.plain_text.split()) if topic.plain_text else 0
    topic.word_count = words
    topic.reading_time_minutes = round(words / 200.0, 1)
    if topic.status == "not_started" and words > 0:
        topic.status = "draft"


def _recompute_section_status(section: TextPlanSection) -> None:
    if not section.topics:
        section.status = "not_started"
        return
    statuses = {t.status for t in section.topics}
    if statuses == {"completed"}:
        section.status = "completed"
    elif "in_review" in statuses or "completed" in statuses or "draft" in statuses:
        section.status = "draft"
    else:
        section.status = "not_started"


def _reindex(items) -> None:
    for i, it in enumerate(items):
        it.order_index = i


def _load(storage: StorageBackend, project_id: str) -> BusinessPlanProject:
    return storage.get_project(project_id)


def _save(storage: StorageBackend, project: BusinessPlanProject) -> None:
    project.text_plan.touch()
    project.touch()
    storage.save_project(project)


def _find_section(doc: TextPlanDocument, section_id: str) -> TextPlanSection:
    for s in doc.sections:
        if s.id == section_id:
            return s
    raise TextPlanError(f"Section {section_id!r} not found")


def _find_topic(doc: TextPlanDocument, topic_id: str):
    for s in doc.sections:
        for t in s.topics:
            if t.id == topic_id:
                return s, t
    raise TextPlanError(f"Topic {topic_id!r} not found")


# --------------------------------------------------------------------------
# inline image migration (legacy attached images -> rich-text image nodes)
# --------------------------------------------------------------------------
def image_node_html(project_id: str, img) -> str:
    """Render a TextPlanImage as an inline rich-text <img> node (data-* attrs)."""
    src = img.url or f"/api/projects/{project_id}/text-plan/images/{img.id}/file"
    return (
        f'<img src="{_html.escape(src)}" data-image-id="{_html.escape(img.id)}" '
        f'data-caption="{_html.escape(img.caption or "")}" '
        f'data-alignment="{_html.escape(img.alignment or "center")}" '
        f'data-width="{int(img.display_width_percentage or 80)}" '
        f'alt="{_html.escape(img.alt_text or "")}" '
        f'title="{_html.escape(img.caption or "")}">'
    )


def migrate_topic_images_into_content(project_id: str, topic) -> bool:
    """Ensure every attached image is referenced inside the topic content.

    Idempotent: only appends image nodes whose ``imageId`` is not already
    present in the content HTML. Returns True if the content changed.
    """
    if not topic.images:
        return False
    html = topic.content_html or ""
    additions = []
    for img in sorted(topic.images, key=lambda i: i.order_index):
        if f'data-image-id="{img.id}"' in html or f"data-image-id='{img.id}'" in html:
            continue
        additions.append(image_node_html(project_id, img))
    if not additions:
        return False
    topic.content_html = html + "".join(additions)
    # Drop stale JSON so the editor re-derives from the migrated HTML.
    topic.content_json = None
    _recompute_topic_metrics(topic)
    return True


def migrate_document(project_id: str, doc: TextPlanDocument) -> bool:
    changed = False
    for section in doc.sections:
        for topic in section.topics:
            if migrate_topic_images_into_content(project_id, topic):
                changed = True
    return changed


# --------------------------------------------------------------------------
# read
# --------------------------------------------------------------------------
def get_text_plan(storage: StorageBackend, project_id: str) -> TextPlanDocument:
    project = _load(storage, project_id)
    if migrate_document(project_id, project.text_plan):
        _save(storage, project)
    return project.text_plan


# --------------------------------------------------------------------------
# sections
# --------------------------------------------------------------------------
def create_section(storage: StorageBackend, project_id: str, data) -> TextPlanSection:
    project = _load(storage, project_id)
    doc = project.text_plan
    section = TextPlanSection(
        title=data.title, subtitle=data.subtitle, description=data.description,
        section_type=data.section_type, guidance_text=data.guidance_text,
        include_in_report=data.include_in_report, page_break_before=data.page_break_before,
    )
    idx = data.order_index if data.order_index is not None else len(doc.sections)
    doc.sections.insert(max(0, min(idx, len(doc.sections))), section)
    _reindex(doc.sections)
    _save(storage, project)
    return section


def update_section(storage: StorageBackend, project_id: str, section_id: str, data) -> TextPlanSection:
    project = _load(storage, project_id)
    section = _find_section(project.text_plan, section_id)
    for field in ("title", "subtitle", "description", "section_type", "guidance_text",
                  "collapsed", "include_in_report", "page_break_before", "status"):
        value = getattr(data, field, None)
        if value is not None:
            setattr(section, field, value)
    section.touch()
    _save(storage, project)
    return section


def delete_section(storage: StorageBackend, project_id: str, section_id: str) -> None:
    project = _load(storage, project_id)
    doc = project.text_plan
    before = len(doc.sections)
    doc.sections = [s for s in doc.sections if s.id != section_id]
    if len(doc.sections) == before:
        raise TextPlanError(f"Section {section_id!r} not found")
    _reindex(doc.sections)
    _save(storage, project)


def duplicate_section(storage: StorageBackend, project_id: str, section_id: str) -> TextPlanSection:
    project = _load(storage, project_id)
    doc = project.text_plan
    section = _find_section(doc, section_id)
    clone = section.model_copy(deep=True)
    _restamp(clone)
    clone.title = f"{section.title} (copy)"
    for topic in clone.topics:
        _restamp(topic)
        topic.section_id = clone.id
        for img in topic.images:
            _restamp(img)
    pos = doc.sections.index(section) + 1
    doc.sections.insert(pos, clone)
    _reindex(doc.sections)
    _save(storage, project)
    return clone


# --------------------------------------------------------------------------
# topics
# --------------------------------------------------------------------------
def create_topic(storage: StorageBackend, project_id: str, data) -> TextPlanTopic:
    project = _load(storage, project_id)
    section = _find_section(project.text_plan, data.section_id)
    topic = TextPlanTopic(
        section_id=section.id, title=data.title, content_html=data.content_html,
        topic_type=data.topic_type, guidance_text=data.guidance_text,
        include_in_report=data.include_in_report,
    )
    _recompute_topic_metrics(topic)
    idx = data.order_index if data.order_index is not None else len(section.topics)
    section.topics.insert(max(0, min(idx, len(section.topics))), topic)
    _reindex(section.topics)
    _recompute_section_status(section)
    _save(storage, project)
    return topic


def update_topic(storage: StorageBackend, project_id: str, topic_id: str, data) -> TextPlanTopic:
    project = _load(storage, project_id)
    section, topic = _find_topic(project.text_plan, topic_id)
    for field in ("title", "content_html", "content_json", "topic_type",
                  "guidance_text", "include_in_report", "status", "priority"):
        value = getattr(data, field, None)
        if value is not None:
            setattr(topic, field, value)
    _recompute_topic_metrics(topic)
    topic.touch()
    _recompute_section_status(section)
    _save(storage, project)
    return topic


def delete_topic(storage: StorageBackend, project_id: str, topic_id: str) -> None:
    project = _load(storage, project_id)
    section, topic = _find_topic(project.text_plan, topic_id)
    section.topics = [t for t in section.topics if t.id != topic_id]
    _reindex(section.topics)
    _recompute_section_status(section)
    _save(storage, project)


def duplicate_topic(storage: StorageBackend, project_id: str, topic_id: str) -> TextPlanTopic:
    project = _load(storage, project_id)
    section, topic = _find_topic(project.text_plan, topic_id)
    clone = topic.model_copy(deep=True)
    _restamp(clone)
    clone.title = f"{topic.title} (copy)"
    clone.section_id = section.id
    for img in clone.images:
        _restamp(img)
    pos = section.topics.index(topic) + 1
    section.topics.insert(pos, clone)
    _reindex(section.topics)
    _save(storage, project)
    return clone


def move_topic(storage: StorageBackend, project_id: str, topic_id: str,
               target_section_id: str, target_order_index: int) -> TextPlanTopic:
    project = _load(storage, project_id)
    doc = project.text_plan
    src_section, topic = _find_topic(doc, topic_id)
    target_section = _find_section(doc, target_section_id)
    src_section.topics = [t for t in src_section.topics if t.id != topic_id]
    _reindex(src_section.topics)
    topic.section_id = target_section.id
    idx = max(0, min(target_order_index, len(target_section.topics)))
    target_section.topics.insert(idx, topic)
    _reindex(target_section.topics)
    _recompute_section_status(src_section)
    _recompute_section_status(target_section)
    topic.touch()
    _save(storage, project)
    return topic


# --------------------------------------------------------------------------
# reorder
# --------------------------------------------------------------------------
def reorder_sections(storage: StorageBackend, project_id: str, ordered_ids: list[str]) -> TextPlanDocument:
    project = _load(storage, project_id)
    doc = project.text_plan
    by_id = {s.id: s for s in doc.sections}
    ordered = [by_id[i] for i in ordered_ids if i in by_id]
    ordered += [s for s in doc.sections if s.id not in set(ordered_ids)]
    doc.sections = ordered
    _reindex(doc.sections)
    _save(storage, project)
    return doc


def reorder_topics(storage: StorageBackend, project_id: str, section_id: str,
                   ordered_ids: list[str]) -> TextPlanSection:
    project = _load(storage, project_id)
    section = _find_section(project.text_plan, section_id)
    by_id = {t.id: t for t in section.topics}
    ordered = [by_id[i] for i in ordered_ids if i in by_id]
    ordered += [t for t in section.topics if t.id not in set(ordered_ids)]
    section.topics = ordered
    _reindex(section.topics)
    _save(storage, project)
    return section


# --------------------------------------------------------------------------
# completion + preview
# --------------------------------------------------------------------------
def calculate_completion(storage: StorageBackend, project_id: str):
    from ..schemas.text_plan import TextPlanCompletion
    doc = _load(storage, project_id).text_plan
    topics = [t for s in doc.sections for t in s.topics]
    completed = [t for t in topics if t.status == "completed"]
    draft = [t for t in topics if t.status in ("draft", "in_review")]
    empty = [t for t in topics if t.word_count == 0]
    word_count = sum(t.word_count for t in topics)
    image_count = sum(len(t.images) for t in topics)

    present_types = {s.section_type for s in doc.sections}
    missing_key = sorted(KEY_SECTION_TYPES - present_types)

    # score: half from "has any content", half from "marked completed"
    percent = 0
    if doc.sections and topics:
        with_content = sum(1 for t in topics if t.word_count > 0)
        content_ratio = with_content / len(topics)
        completed_ratio = len(completed) / len(topics)
        percent = round((content_ratio * 0.6 + completed_ratio * 0.4) * 100)

    warnings: list[str] = []
    if not doc.sections:
        warnings.append("No sections yet — generate a suggested outline or start from a template.")
    if empty:
        warnings.append(f"{len(empty)} topic(s) have no written content.")
    for key in missing_key:
        warnings.append(f"Recommended section missing: {key.replace('_', ' ').title()}.")

    return TextPlanCompletion(
        project_id=project_id, completion_percent=percent,
        section_count=len(doc.sections), topic_count=len(topics),
        completed_topics=len(completed), draft_topics=len(draft), empty_topics=len(empty),
        word_count=word_count, image_count=image_count,
        sections_in_report=sum(1 for s in doc.sections if s.include_in_report),
        topics_in_report=sum(1 for t in topics if t.include_in_report),
        missing_key_sections=missing_key, warnings=warnings,
    )


def get_preview(storage: StorageBackend, project_id: str):
    from ..schemas.text_plan import (
        TextPlanPreview,
        TextPlanPreviewSection,
        TextPlanPreviewTopic,
    )
    doc = _load(storage, project_id).text_plan
    sections = []
    topic_total = 0
    for s in doc.sections:
        if not s.include_in_report:
            continue
        prev_topics = []
        for t in s.topics:
            if not t.include_in_report:
                continue
            topic_total += 1
            prev_topics.append(TextPlanPreviewTopic(
                id=t.id, title=t.title, content_html=t.content_html, status=t.status,
                word_count=t.word_count, include_in_report=t.include_in_report,
                image_count=len(t.images),
            ))
        sections.append(TextPlanPreviewSection(
            id=s.id, title=s.title, description=s.description,
            include_in_report=s.include_in_report, status=s.status, topics=prev_topics,
        ))
    return TextPlanPreview(
        project_id=project_id, title=doc.title or "Written Business Plan",
        section_count=len(sections), topic_count=topic_total, sections=sections,
    )


# --------------------------------------------------------------------------
# misc
# --------------------------------------------------------------------------
def _restamp(model) -> None:
    from ..utils.ids import new_id
    model.id = new_id()
    model.created_at = utcnow()
    model.updated_at = utcnow()


def project_or_404(storage: StorageBackend, project_id: str) -> BusinessPlanProject:
    try:
        return storage.get_project(project_id)
    except NotFoundError as exc:
        raise TextPlanError(str(exc))
