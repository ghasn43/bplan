"""Project-level routes: CRUD, completion, review, export."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..models import BusinessPlanProject, CompletionReport, ProjectSummary, ReviewStatus
from ..services import ProjectService, build_completion_report, build_review_status
from ..storage.base import NotFoundError
from .deps import get_service, project_or_404

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


@router.get("", response_model=list[ProjectSummary])
def list_projects(service: ProjectService = Depends(get_service)):
    return service.list_summaries()


@router.post("", response_model=BusinessPlanProject, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, service: ProjectService = Depends(get_service)):
    project = BusinessPlanProject(name=payload.name)
    return service.create(project)


@router.get("/{project_id}", response_model=BusinessPlanProject)
def get_project(project_id: str, service: ProjectService = Depends(get_service)):
    return project_or_404(project_id, service)


@router.put("/{project_id}", response_model=BusinessPlanProject)
def replace_project(
    project_id: str,
    payload: BusinessPlanProject,
    service: ProjectService = Depends(get_service),
):
    try:
        return service.replace(project_id, payload)
    except NotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Project {project_id!r} not found")


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, service: ProjectService = Depends(get_service)):
    try:
        service.delete(project_id)
    except NotFoundError:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Project {project_id!r} not found")


@router.get("/{project_id}/completion", response_model=CompletionReport)
def get_completion(project_id: str, service: ProjectService = Depends(get_service)):
    project = project_or_404(project_id, service)
    return build_completion_report(project)


@router.get("/{project_id}/review", response_model=ReviewStatus)
def get_review(project_id: str, service: ProjectService = Depends(get_service)):
    project = project_or_404(project_id, service)
    return build_review_status(project)


@router.get("/{project_id}/export-json")
def export_json(project_id: str, service: ProjectService = Depends(get_service)):
    project = project_or_404(project_id, service)
    filename = f"{project.name.replace(' ', '_')}_assumptions.json"
    return JSONResponse(
        content=project.model_dump(mode="json"),
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
