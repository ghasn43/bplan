"""Persistence layer.

The service layer depends only on :class:`StorageBackend`. Today the concrete
implementation is :class:`JSONStorage`; a future ``PostgresStorage`` can be
dropped in here without touching routes or services.
"""
from __future__ import annotations

from ..config import settings
from .base import StorageBackend
from .company_storage import CompanyStorage
from .json_storage import JSONStorage

_backend: StorageBackend | None = None
_company_backend: CompanyStorage | None = None


def get_storage() -> StorageBackend:
    """FastAPI dependency returning the process-wide storage backend."""
    global _backend
    if _backend is None:
        if settings.storage_backend == "json":
            _backend = JSONStorage(settings.data_dir)
        else:  # pragma: no cover - future upgrade path
            raise RuntimeError(
                f"Unsupported storage backend: {settings.storage_backend!r}"
            )
    return _backend


def get_company_storage() -> CompanyStorage:
    """FastAPI dependency returning the process-wide company storage."""
    global _company_backend
    if _company_backend is None:
        _company_backend = CompanyStorage(settings.data_dir)
    return _company_backend


__all__ = ["StorageBackend", "JSONStorage", "CompanyStorage", "get_storage", "get_company_storage"]
