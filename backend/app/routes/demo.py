"""Demo-company routes: preview + load/reset the AquaPure scenario."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..models import BusinessPlanProject
from ..services import demo
from ..storage import get_company_storage, get_storage
from ..storage.base import StorageBackend
from ..storage.company_storage import CompanyStorage

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/aquapure-preview")
def aquapure_preview(storage: StorageBackend = Depends(get_storage)) -> dict:
    """Metadata for the 'Load Demo Company' card (no side effects)."""
    return demo.aquapure_preview(storage)


@router.post("/load-aquapure", response_model=BusinessPlanProject)
def load_aquapure(storage: StorageBackend = Depends(get_storage),
                  companies: CompanyStorage = Depends(get_company_storage)) -> BusinessPlanProject:
    """Create or reset the AquaPure Smart Filters FZE demo company + project."""
    return demo.load_aquapure(storage, companies)
