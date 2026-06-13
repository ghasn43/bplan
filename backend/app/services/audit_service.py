"""Audit logging helper."""
from __future__ import annotations

from ..models import AuditLog
from ..storage import get_audit_storage


def log(action: str, *, user=None, entity_type=None, entity_id=None, company_id=None,
        project_id=None, details=None, request=None) -> None:
    ip = ua = None
    if request is not None:
        ip = request.client.host if request.client else None
        ua = request.headers.get("user-agent")
    get_audit_storage().append(AuditLog(
        action=action, user_id=getattr(user, "id", None),
        entity_type=entity_type, entity_id=entity_id, company_id=company_id,
        project_id=project_id, ip_address=ip, user_agent=ua, details=details,
    ))


def recent(limit: int = 500):
    return get_audit_storage().list(limit)
