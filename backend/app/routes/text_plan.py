"""Textual business plan routes (sections, topics, images, outline templates)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from ..models.text_plan import TextPlanDocument, TextPlanImage, TextPlanSection, TextPlanTopic
from ..schemas.text_plan import (
    ApplyOutlineTemplateRequest,
    ImageUpdate,
    MoveTopicRequest,
    OutlineSuggestionResponse,
    OutlineTemplateInfo,
    ReorderSectionsRequest,
    ReorderTopicsRequest,
    SectionCreate,
    SectionUpdate,
    TextPlanCompletion,
    TextPlanPreview,
    TopicCreate,
    TopicUpdate,
)
from ..services import business_plan_outline_service as outline
from ..services import text_plan_image_service as imgsvc
from ..services import text_plan_service as tp
from ..storage import get_storage
from ..storage.base import NotFoundError, StorageBackend

router = APIRouter(prefix="/projects/{project_id}/text-plan", tags=["text-plan"])


def _project_or_404(storage: StorageBackend, project_id: str):
    try:
        return storage.get_project(project_id)
    except NotFoundError:
        raise HTTPException(status_code=404, detail=f"Project {project_id!r} not found")


def _guard(fn, *args):
    try:
        return fn(*args)
    except tp.TextPlanError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except imgsvc.ImageError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# --------------------------------------------------------------------------
# document / preview / completion
# --------------------------------------------------------------------------
@router.get("", response_model=TextPlanDocument)
def get_text_plan(project_id: str, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return tp.get_text_plan(storage, project_id)


@router.get("/preview", response_model=TextPlanPreview)
def preview(project_id: str, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return tp.get_preview(storage, project_id)


@router.get("/completion", response_model=TextPlanCompletion)
def completion(project_id: str, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return tp.calculate_completion(storage, project_id)


# --------------------------------------------------------------------------
# sections
# --------------------------------------------------------------------------
@router.post("/sections", response_model=TextPlanSection, status_code=status.HTTP_201_CREATED)
def create_section(project_id: str, body: SectionCreate, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.create_section, storage, project_id, body)


@router.put("/sections/{section_id}", response_model=TextPlanSection)
def update_section(project_id: str, section_id: str, body: SectionUpdate,
                   storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.update_section, storage, project_id, section_id, body)


@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(project_id: str, section_id: str, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    _guard(tp.delete_section, storage, project_id, section_id)
    return None


@router.post("/sections/{section_id}/duplicate", response_model=TextPlanSection)
def duplicate_section(project_id: str, section_id: str, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.duplicate_section, storage, project_id, section_id)


# --------------------------------------------------------------------------
# topics
# --------------------------------------------------------------------------
@router.post("/topics", response_model=TextPlanTopic, status_code=status.HTTP_201_CREATED)
def create_topic(project_id: str, body: TopicCreate, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.create_topic, storage, project_id, body)


@router.put("/topics/{topic_id}", response_model=TextPlanTopic)
def update_topic(project_id: str, topic_id: str, body: TopicUpdate,
                 storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.update_topic, storage, project_id, topic_id, body)


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(project_id: str, topic_id: str, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    _guard(tp.delete_topic, storage, project_id, topic_id)
    return None


@router.post("/topics/{topic_id}/duplicate", response_model=TextPlanTopic)
def duplicate_topic(project_id: str, topic_id: str, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.duplicate_topic, storage, project_id, topic_id)


# --------------------------------------------------------------------------
# reorder / move
# --------------------------------------------------------------------------
@router.put("/reorder-sections", response_model=TextPlanDocument)
def reorder_sections(project_id: str, body: ReorderSectionsRequest,
                     storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.reorder_sections, storage, project_id, body.ordered_section_ids)


@router.put("/reorder-topics", response_model=TextPlanSection)
def reorder_topics(project_id: str, body: ReorderTopicsRequest,
                   storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.reorder_topics, storage, project_id, body.section_id, body.ordered_topic_ids)


@router.put("/move-topic", response_model=TextPlanTopic)
def move_topic(project_id: str, body: MoveTopicRequest, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(tp.move_topic, storage, project_id, body.topic_id,
                  body.target_section_id, body.target_order_index)


# --------------------------------------------------------------------------
# images
# --------------------------------------------------------------------------
@router.post("/topics/{topic_id}/images", response_model=TextPlanImage, status_code=status.HTTP_201_CREATED)
async def upload_image(project_id: str, topic_id: str, file: UploadFile = File(...),
                       storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    content = await file.read()
    try:
        return imgsvc.upload_topic_image(
            storage, project_id, topic_id, content=content,
            original_file_name=file.filename or "image",
            content_type=file.content_type or "image/png",
        )
    except tp.TextPlanError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except imgsvc.ImageError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.put("/topics/{topic_id}/images/{image_id}", response_model=TextPlanImage)
def update_image(project_id: str, topic_id: str, image_id: str, body: ImageUpdate,
                 storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return _guard(imgsvc.update_topic_image_metadata, storage, project_id, topic_id, image_id, body)


@router.delete("/topics/{topic_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(project_id: str, topic_id: str, image_id: str,
                 storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    _guard(imgsvc.delete_topic_image, storage, project_id, topic_id, image_id)
    return None


@router.get("/topics/{topic_id}/images/{image_id}/file")
def get_image_file(project_id: str, topic_id: str, image_id: str,
                   storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    img = _guard(imgsvc.get_image_record, storage, project_id, topic_id, image_id)
    path = imgsvc.image_file_path(project_id, img.file_name)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image file is missing")
    return FileResponse(path, media_type=img.mime_type or "image/png")


@router.get("/images/{image_id}/file")
def get_image_file_by_id(project_id: str, image_id: str, storage: StorageBackend = Depends(get_storage)):
    """Topic-independent image serving (used by inline rich-text image nodes)."""
    project = _project_or_404(storage, project_id)
    _topic, img = imgsvc.find_image(project, image_id)
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    path = imgsvc.image_file_path(project_id, img.file_name)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image file is missing")
    return FileResponse(path, media_type=img.mime_type or "image/png",
                        filename=img.original_file_name or img.file_name)


# --------------------------------------------------------------------------
# templates / outline
# --------------------------------------------------------------------------
@router.get("/templates", response_model=list[OutlineTemplateInfo])
def list_templates(project_id: str, storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    return outline.list_outline_templates()


@router.get("/outline-suggestions", response_model=OutlineSuggestionResponse)
def outline_suggestions(project_id: str, storage: StorageBackend = Depends(get_storage)):
    project = _project_or_404(storage, project_id)
    return outline.generate_outline_suggestions(project)


@router.post("/apply-outline-template", response_model=TextPlanDocument)
def apply_template(project_id: str, body: ApplyOutlineTemplateRequest,
                   storage: StorageBackend = Depends(get_storage)):
    _project_or_404(storage, project_id)
    try:
        return outline.apply_outline_template(storage, project_id, body)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
