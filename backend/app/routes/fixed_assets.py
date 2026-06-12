"""Fixed-asset depreciation schedule + summary + single-asset routes.

(List/create/update/delete are provided by the generic section router under
the same ``/fixed-assets`` prefix.)
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models import FixedAsset
from ..schemas.fixed_assets import DepreciationSchedule, FixedAssetSummary
from ..services import ProjectService
from ..services import fixed_asset_service as fas
from .deps import get_service, project_or_404

router = APIRouter(prefix="/projects/{project_id}/fixed-assets", tags=["fixed-assets"])

View = Query("annual", pattern="^(monthly|annual)$")


@router.get("/depreciation-schedule", response_model=DepreciationSchedule, response_model_exclude_none=True)
def depreciation_schedule(project_id: str, view: str = View, service: ProjectService = Depends(get_service)):
    project = project_or_404(project_id, service)
    return fas.generate_depreciation_schedule(project, view)


@router.get("/summary", response_model=FixedAssetSummary)
def fixed_asset_summary(project_id: str, service: ProjectService = Depends(get_service)):
    project = project_or_404(project_id, service)
    return fas.build_summary(project)


@router.get("/{asset_id}", response_model=FixedAsset)
def get_fixed_asset(project_id: str, asset_id: str, service: ProjectService = Depends(get_service)):
    project = project_or_404(project_id, service)
    for asset in project.fixed_assets:
        if asset.id == asset_id:
            return asset
    raise HTTPException(status.HTTP_404_NOT_FOUND, f"Asset {asset_id!r} not found")
