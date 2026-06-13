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
from .user_storage import AuditStorage, UserStorage

_backend: StorageBackend | None = None
_company_backend: CompanyStorage | None = None
_user_backend: UserStorage | None = None
_audit_backend: AuditStorage | None = None


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


def get_user_storage() -> UserStorage:
    global _user_backend
    if _user_backend is None:
        _user_backend = UserStorage(settings.data_dir)
    return _user_backend


def get_audit_storage() -> AuditStorage:
    global _audit_backend
    if _audit_backend is None:
        _audit_backend = AuditStorage(settings.data_dir)
    return _audit_backend


__all__ = [
    "StorageBackend", "JSONStorage", "CompanyStorage", "UserStorage", "AuditStorage",
    "get_storage", "get_company_storage", "get_user_storage", "get_audit_storage",
]
