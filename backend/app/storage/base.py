"""Abstract storage interface.

Keeping this interface narrow (it deals only in whole project documents)
makes the JSON → PostgreSQL migration a self-contained task: implement the
five methods against SQLAlchemy/asyncpg and register it in ``__init__``.
"""
from __future__ import annotations

import abc

from ..models import BusinessPlanProject


class StorageError(Exception):
    """Base class for storage-layer errors."""


class NotFoundError(StorageError):
    """Raised when a requested project does not exist."""


class CorruptProjectError(StorageError):
    """Raised when a stored project cannot be parsed/validated.

    Usually means the file was written by an older schema version.
    """


class StorageBackend(abc.ABC):
    @abc.abstractmethod
    def list_projects(self) -> list[BusinessPlanProject]:
        ...

    @abc.abstractmethod
    def get_project(self, project_id: str) -> BusinessPlanProject:
        """Return a project or raise :class:`NotFoundError`."""

    @abc.abstractmethod
    def save_project(self, project: BusinessPlanProject) -> BusinessPlanProject:
        """Insert or update a project document."""

    @abc.abstractmethod
    def delete_project(self, project_id: str) -> None:
        ...

    @abc.abstractmethod
    def exists(self, project_id: str) -> bool:
        ...
