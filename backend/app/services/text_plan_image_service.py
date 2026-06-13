"""Topic image upload/management for the textual business plan.

Images are stored on disk under ``backend/uploads/projects/{project_id}/text-plan/``
and referenced from the owning topic. The report generator reads the files
directly; the frontend loads them via the image URL route.
"""
from __future__ import annotations

import io
from pathlib import Path

from ..models.text_plan import TextPlanImage
from ..storage.base import StorageBackend
from ..utils.ids import new_id
from .text_plan_service import _find_topic, _reindex, _save

UPLOADS_ROOT = Path(__file__).resolve().parent.parent.parent / "uploads"
ALLOWED_MIME = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"}
EXT_BY_MIME = {"image/png": ".png", "image/jpeg": ".jpg", "image/jpg": ".jpg",
               "image/gif": ".gif", "image/webp": ".webp"}
MAX_BYTES = 8 * 1024 * 1024


class ImageError(Exception):
    """Invalid image operation (mapped to HTTP 400/404)."""


def _topic_dir(project_id: str) -> Path:
    safe = "".join(c for c in project_id if c.isalnum() or c in "._-") or "project"
    d = UPLOADS_ROOT / "projects" / safe / "text-plan"
    d.mkdir(parents=True, exist_ok=True)
    return d


def image_url(project_id: str, image_id: str) -> str:
    """Topic-independent URL so the rich-text node keeps working when a topic
    is moved/duplicated. Resolved by :func:`find_image`."""
    return f"/api/projects/{project_id}/text-plan/images/{image_id}/file"


def image_file_path(project_id: str, file_name: str) -> Path:
    return _topic_dir(project_id) / file_name


def find_image(project, image_id: str):
    """Return (topic, image) for an image id anywhere in the project, or (None, None)."""
    for section in project.text_plan.sections:
        for topic in section.topics:
            for img in topic.images:
                if img.id == image_id:
                    return topic, img
    return None, None


def build_image_index(project) -> dict:
    """image_id -> {file_path, mime_type, caption, alignment, width_pct} for all images."""
    index: dict[str, dict] = {}
    for section in project.text_plan.sections:
        for topic in section.topics:
            for img in topic.images:
                index[img.id] = {
                    "file_path": img.file_path, "mime_type": img.mime_type,
                    "caption": img.caption, "alignment": img.alignment,
                    "width_pct": img.display_width_percentage, "alt_text": img.alt_text,
                }
    return index


def upload_topic_image(storage: StorageBackend, project_id: str, topic_id: str,
                       *, content: bytes, original_file_name: str, content_type: str) -> TextPlanImage:
    if content_type not in ALLOWED_MIME:
        raise ImageError(f"Unsupported image type {content_type!r}. Use PNG, JPG, GIF or WEBP.")
    if len(content) > MAX_BYTES:
        raise ImageError("Image is too large (max 8 MB).")

    project = storage.get_project(project_id)
    _section, topic = _find_topic(project.text_plan, topic_id)

    image_id = new_id()
    ext = EXT_BY_MIME.get(content_type, ".png")
    file_name = f"{image_id}{ext}"
    path = _topic_dir(project_id) / file_name
    path.write_bytes(content)

    width = height = None
    try:
        from PIL import Image
        with Image.open(io.BytesIO(content)) as im:
            width, height = im.size
    except Exception:
        pass

    img = TextPlanImage(
        id=image_id, file_name=file_name, original_file_name=original_file_name,
        file_path=str(path), url=image_url(project_id, image_id),
        mime_type=content_type, file_size=len(content), width=width, height=height,
        order_index=len(topic.images),
    )
    topic.images.append(img)
    topic.touch()
    _save(storage, project)
    return img


def update_topic_image_metadata(storage: StorageBackend, project_id: str, topic_id: str,
                                image_id: str, data) -> TextPlanImage:
    project = storage.get_project(project_id)
    _section, topic = _find_topic(project.text_plan, topic_id)
    img = next((i for i in topic.images if i.id == image_id), None)
    if not img:
        raise ImageError(f"Image {image_id!r} not found")
    for field in ("caption", "alt_text", "alignment", "display_width_percentage", "order_index"):
        value = getattr(data, field, None)
        if value is not None:
            setattr(img, field, value)
    img.touch()
    topic.images.sort(key=lambda i: i.order_index)
    _reindex(topic.images)
    _save(storage, project)
    return img


def delete_topic_image(storage: StorageBackend, project_id: str, topic_id: str, image_id: str) -> None:
    project = storage.get_project(project_id)
    _section, topic = _find_topic(project.text_plan, topic_id)
    img = next((i for i in topic.images if i.id == image_id), None)
    if not img:
        raise ImageError(f"Image {image_id!r} not found")
    try:
        p = Path(img.file_path)
        if p.exists():
            p.unlink()
    except Exception:
        pass
    topic.images = [i for i in topic.images if i.id != image_id]
    _reindex(topic.images)
    _save(storage, project)


def get_image_record(storage: StorageBackend, project_id: str, topic_id: str, image_id: str) -> TextPlanImage:
    project = storage.get_project(project_id)
    _section, topic = _find_topic(project.text_plan, topic_id)
    img = next((i for i in topic.images if i.id == image_id), None)
    if not img:
        raise ImageError(f"Image {image_id!r} not found")
    return img
