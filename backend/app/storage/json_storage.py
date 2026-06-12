"""JSON-file storage backend.

One file per project under ``data/projects/<id>.json``. Writes are atomic
(temp file + replace) and guarded by a process-level lock so concurrent
requests cannot corrupt a document.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from ..models import BusinessPlanProject
from .base import CorruptProjectError, NotFoundError, StorageBackend


class JSONStorage(StorageBackend):
    def __init__(self, data_dir: Path) -> None:
        self._dir = Path(data_dir) / "projects"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    # -- helpers ----------------------------------------------------------
    def _path(self, project_id: str) -> Path:
        return self._dir / f"{project_id}.json"

    def _read(self, path: Path) -> BusinessPlanProject:
        data = json.loads(path.read_text(encoding="utf-8"))
        return BusinessPlanProject.model_validate(data)

    # -- interface --------------------------------------------------------
    def list_projects(self) -> list[BusinessPlanProject]:
        with self._lock:
            projects = []
            for path in self._dir.glob("*.json"):
                try:
                    projects.append(self._read(path))
                except Exception:  # skip corrupt / partial files
                    continue
        projects.sort(key=lambda p: p.updated_at, reverse=True)
        return projects

    def get_project(self, project_id: str) -> BusinessPlanProject:
        with self._lock:
            path = self._path(project_id)
            if not path.exists():
                raise NotFoundError(f"Project {project_id!r} not found")
            try:
                return self._read(path)
            except Exception as exc:  # JSON or schema validation failure
                raise CorruptProjectError(
                    f"Project file {path.name} could not be read (likely saved by an "
                    f"older app version). Delete it from the data directory and retry. "
                    f"Cause: {type(exc).__name__}"
                ) from exc

    def save_project(self, project: BusinessPlanProject) -> BusinessPlanProject:
        with self._lock:
            path = self._path(project.id)
            tmp = path.with_suffix(".json.tmp")
            payload = project.model_dump(mode="json")
            tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, path)
        return project

    def delete_project(self, project_id: str) -> None:
        with self._lock:
            path = self._path(project_id)
            if not path.exists():
                raise NotFoundError(f"Project {project_id!r} not found")
            path.unlink()

    def exists(self, project_id: str) -> bool:
        return self._path(project_id).exists()
