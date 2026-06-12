"""Generic section routers generated from the section registry.

Rather than hand-writing 13 near-identical CRUD modules, we build the routers
from :data:`COLLECTION_SECTIONS` / :data:`SINGLETON_SECTIONS`. The resulting
OpenAPI surface still matches the spec exactly, e.g.::

    GET    /api/projects/{project_id}/products
    POST   /api/projects/{project_id}/products
    PUT    /api/projects/{project_id}/products/{item_id}
    DELETE /api/projects/{project_id}/products/{item_id}
    GET    /api/projects/{project_id}/setup
    PUT    /api/projects/{project_id}/setup
"""
# NOTE: deliberately no ``from __future__ import annotations`` here — the
# generic routers rely on real class objects (not stringified forward refs)
# in the endpoint annotations so FastAPI can resolve request-body models.
from fastapi import APIRouter, Body, Depends, HTTPException, status

from ..services import ProjectService
from ..services.projects import SectionError
from ..services.registry import COLLECTION_SECTIONS, SINGLETON_SECTIONS, SectionSpec
from ..storage.base import NotFoundError
from .deps import get_service


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, detail)


def _build_collection_router(spec: SectionSpec) -> APIRouter:
    router = APIRouter(
        prefix="/projects/{project_id}/" + spec.key,
        tags=[spec.label],
    )
    Model = spec.model

    @router.get("", response_model=list[Model])
    def list_items(project_id: str, service: ProjectService = Depends(get_service)):
        try:
            return service.list_items(project_id, spec.key)
        except NotFoundError:
            raise _not_found(f"Project {project_id!r} not found")

    @router.post("", response_model=Model, status_code=status.HTTP_201_CREATED)
    def add_item(project_id: str, item: Model = Body(...), service: ProjectService = Depends(get_service)):  # type: ignore[valid-type]
        try:
            return service.add_item(project_id, spec.key, item)
        except NotFoundError:
            raise _not_found(f"Project {project_id!r} not found")

    @router.put("/{item_id}", response_model=Model)
    def update_item(
        project_id: str,
        item_id: str,
        item: Model = Body(...),  # type: ignore[valid-type]
        service: ProjectService = Depends(get_service),
    ):
        try:
            return service.update_item(project_id, spec.key, item_id, item)
        except NotFoundError:
            raise _not_found(f"Project {project_id!r} not found")
        except SectionError as exc:
            raise _not_found(str(exc))

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(project_id: str, item_id: str, service: ProjectService = Depends(get_service)):
        try:
            service.delete_item(project_id, spec.key, item_id)
        except NotFoundError:
            raise _not_found(f"Project {project_id!r} not found")
        except SectionError as exc:
            raise _not_found(str(exc))

    return router


def _build_singleton_router(spec: SectionSpec) -> APIRouter:
    router = APIRouter(
        prefix="/projects/{project_id}/" + spec.key,
        tags=[spec.label],
    )
    Model = spec.model

    @router.get("", response_model=Model | None)
    def get_section(project_id: str, service: ProjectService = Depends(get_service)):
        try:
            return service.get_singleton(project_id, spec.key)
        except NotFoundError:
            raise _not_found(f"Project {project_id!r} not found")

    @router.put("", response_model=Model)
    def put_section(project_id: str, payload: Model = Body(...), service: ProjectService = Depends(get_service)):  # type: ignore[valid-type]
        try:
            return service.put_singleton(project_id, spec.key, payload)
        except NotFoundError:
            raise _not_found(f"Project {project_id!r} not found")

    return router


def build_section_routers() -> list[APIRouter]:
    routers: list[APIRouter] = []
    for spec in SINGLETON_SECTIONS.values():
        routers.append(_build_singleton_router(spec))
    for spec in COLLECTION_SECTIONS.values():
        routers.append(_build_collection_router(spec))
    return routers
