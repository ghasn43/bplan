"""Excel financial model export routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from ..schemas.excel_export import ExcelExportFile, ExcelExportPreview, ExcelExportRequest, ExcelExportResponse
from ..services import ProjectService
from ..services import excel_model_service as xl
from .deps import get_service, project_or_404

router = APIRouter(prefix="/projects/{project_id}/exports", tags=["exports"])

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _download_url(project_id: str, export_id: str) -> str:
    return f"/api/projects/{project_id}/exports/{export_id}/download"


def _to_response(project_id: str, f: ExcelExportFile) -> ExcelExportResponse:
    return ExcelExportResponse(**f.model_dump(), download_url=_download_url(project_id, f.export_id))


@router.get("/excel-financial-model/preview", response_model=ExcelExportPreview)
def preview(project_id: str, scenario: str = "base", protect_formulas: bool = True,
            service: ProjectService = Depends(get_service)):
    project = project_or_404(project_id, service)
    req = ExcelExportRequest(scenario=scenario, protect_formulas=protect_formulas)
    return xl.build_preview(project, req)


@router.post("/excel-financial-model", response_model=ExcelExportResponse)
def generate(project_id: str, request: ExcelExportRequest, service: ProjectService = Depends(get_service)):
    project = project_or_404(project_id, service)
    try:
        entry = xl.generate_excel_financial_model(project, request)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Excel model generation failed: {type(exc).__name__}: {exc}")
    return _to_response(project_id, entry)


@router.get("", response_model=list[ExcelExportResponse])
def list_exports(project_id: str, service: ProjectService = Depends(get_service)):
    project_or_404(project_id, service)
    out = []
    for entry in xl.load_index(project_id):
        try:
            out.append(_to_response(project_id, ExcelExportFile(**entry)))
        except Exception:
            continue
    return out


@router.get("/{export_id}/download")
def download(project_id: str, export_id: str, service: ProjectService = Depends(get_service)):
    project_or_404(project_id, service)
    entry = next((e for e in xl.load_index(project_id) if e.get("export_id") == export_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Export not found")
    path = xl.export_path(project_id, entry["file_name"])
    if not path.exists():
        raise HTTPException(status_code=404, detail="Export file is missing")
    return FileResponse(path, media_type=XLSX_MIME, filename=entry["file_name"])


@router.delete("/{export_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(project_id: str, export_id: str, service: ProjectService = Depends(get_service)):
    project_or_404(project_id, service)
    if not xl.delete_export(project_id, export_id):
        raise HTTPException(status_code=404, detail="Export not found")
    return None
