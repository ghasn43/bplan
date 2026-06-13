"""JSON-file storage for companies (one file per company under data/companies/).

Mirrors :class:`JSONStorage` for projects so a future relational migration is a
self-contained task.
"""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from ..models import Company
from .base import NotFoundError


class CompanyStorage:
    def __init__(self, data_dir: Path) -> None:
        self._dir = Path(data_dir) / "companies"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _path(self, company_id: str) -> Path:
        return self._dir / f"{company_id}.json"

    def list_companies(self) -> list[Company]:
        with self._lock:
            out = []
            for path in self._dir.glob("*.json"):
                try:
                    out.append(Company.model_validate(json.loads(path.read_text(encoding="utf-8"))))
                except Exception:
                    continue
        out.sort(key=lambda c: c.updated_at, reverse=True)
        return out

    def get_company(self, company_id: str) -> Company:
        with self._lock:
            path = self._path(company_id)
            if not path.exists():
                raise NotFoundError(f"Company {company_id!r} not found")
            return Company.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def save_company(self, company: Company) -> Company:
        with self._lock:
            path = self._path(company.id)
            tmp = path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(company.model_dump(mode="json"), indent=2, ensure_ascii=False),
                           encoding="utf-8")
            os.replace(tmp, path)
        return company

    def delete_company(self, company_id: str) -> None:
        with self._lock:
            path = self._path(company_id)
            if path.exists():
                path.unlink()

    def exists(self, company_id: str) -> bool:
        return self._path(company_id).exists()
