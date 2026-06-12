"""Project service: orchestrates storage + section mutations.

Routes stay thin; all read-modify-write logic for the aggregate document
lives here so it can be reused and unit-tested independently.
"""
from __future__ import annotations

from typing import Any

from ..models import (
    BusinessPlanProject,
    ProjectSummary,
)
from ..storage.base import NotFoundError, StorageBackend
from ..utils.ids import utcnow
from .completion import build_completion_report
from .registry import ALL_SECTIONS, COLLECTION_SECTIONS, SINGLETON_SECTIONS


class SectionError(Exception):
    """Raised for invalid section / item operations (mapped to HTTP 400/404)."""


class ProjectService:
    def __init__(self, storage: StorageBackend) -> None:
        self.storage = storage

    # -- project CRUD -----------------------------------------------------
    def list_summaries(self) -> list[ProjectSummary]:
        summaries = []
        for p in self.storage.list_projects():
            completion = build_completion_report(p)
            summaries.append(
                ProjectSummary(
                    id=p.id,
                    name=p.name,
                    business_name=p.setup.business_name if p.setup else None,
                    currency=p.setup.currency if p.setup else None,
                    projection_period=(
                        p.setup.projection_period.value if p.setup else None
                    ),
                    completion_percent=completion.completion_percent,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                )
            )
        return summaries

    def create(self, project: BusinessPlanProject) -> BusinessPlanProject:
        return self.storage.save_project(project)

    def get(self, project_id: str) -> BusinessPlanProject:
        return self.storage.get_project(project_id)

    def replace(self, project_id: str, incoming: BusinessPlanProject) -> BusinessPlanProject:
        existing = self.storage.get_project(project_id)
        incoming.id = existing.id
        incoming.created_at = existing.created_at
        incoming.updated_at = utcnow()
        return self.storage.save_project(incoming)

    def update_name(self, project_id: str, name: str) -> BusinessPlanProject:
        project = self.storage.get_project(project_id)
        project.name = name
        project.touch()
        return self.storage.save_project(project)

    def delete(self, project_id: str) -> None:
        self.storage.delete_project(project_id)

    # -- singleton sections (setup, working-capital, tax, kpis, financing)
    def get_singleton(self, project_id: str, key: str) -> Any:
        spec = SINGLETON_SECTIONS[key]
        project = self.storage.get_project(project_id)
        return getattr(project, spec.attr)

    def put_singleton(self, project_id: str, key: str, value: Any) -> Any:
        spec = SINGLETON_SECTIONS[key]
        project = self.storage.get_project(project_id)
        if hasattr(value, "touch"):
            value.touch()
        setattr(project, spec.attr, value)
        project.touch()
        self.storage.save_project(project)
        return getattr(project, spec.attr)

    # -- collection sections ---------------------------------------------
    def list_items(self, project_id: str, key: str) -> list[Any]:
        spec = COLLECTION_SECTIONS[key]
        project = self.storage.get_project(project_id)
        return getattr(project, spec.attr)

    def add_item(self, project_id: str, key: str, item: Any) -> Any:
        spec = COLLECTION_SECTIONS[key]
        project = self.storage.get_project(project_id)
        getattr(project, spec.attr).append(item)
        project.touch()
        self.storage.save_project(project)
        return item

    def update_item(self, project_id: str, key: str, item_id: str, item: Any) -> Any:
        spec = COLLECTION_SECTIONS[key]
        project = self.storage.get_project(project_id)
        collection = getattr(project, spec.attr)
        for idx, existing in enumerate(collection):
            if existing.id == item_id:
                item.id = item_id
                item.created_at = existing.created_at
                item.updated_at = utcnow()
                collection[idx] = item
                project.touch()
                self.storage.save_project(project)
                return item
        raise SectionError(f"Item {item_id!r} not found in section {key!r}")

    def delete_item(self, project_id: str, key: str, item_id: str) -> None:
        spec = COLLECTION_SECTIONS[key]
        project = self.storage.get_project(project_id)
        collection = getattr(project, spec.attr)
        new_collection = [i for i in collection if i.id != item_id]
        if len(new_collection) == len(collection):
            raise SectionError(f"Item {item_id!r} not found in section {key!r}")
        setattr(project, spec.attr, new_collection)
        project.touch()
        self.storage.save_project(project)
