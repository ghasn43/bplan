"""Admin audit-log route."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..dependencies.auth import require_admin
from ..models import User
from ..schemas.user import AuditLogPublic
from ..services import audit_service

router = APIRouter(prefix="/admin/audit-log", tags=["admin"])


@router.get("", response_model=list[AuditLogPublic])
def audit_log(limit: int = 300, admin: User = Depends(require_admin)):
    return [
        AuditLogPublic(
            id=e.id, user_id=e.user_id, action=e.action, entity_type=e.entity_type,
            entity_id=e.entity_id, company_id=e.company_id, project_id=e.project_id,
            details=e.details, created_at=e.created_at,
        )
        for e in audit_service.recent(limit)
    ]
