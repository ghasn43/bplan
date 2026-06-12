"""Shared FastAPI dependencies and error mapping."""
from __future__ import annotations

from fastapi import Depends, HTTPException, status

from ..services import ProjectService
from ..storage import get_storage
from ..storage.base import NotFoundError, StorageBackend


def get_service(storage: StorageBackend = Depends(get_storage)) -> ProjectService:
    return ProjectService(storage)


def project_or_404(project_id: str, service: ProjectService):
    try:
        return service.get(project_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id!r} not found",
        )
