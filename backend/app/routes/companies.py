"""Company routes: company CRUD + a company's projects."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ..models import BusinessPlanProject, Company, CompanySummary, ProjectSummary
from ..services.companies import CompanyService
from ..storage import get_company_storage, get_storage
from ..storage.base import NotFoundError, StorageBackend
from ..storage.company_storage import CompanyStorage

router = APIRouter(prefix="/companies", tags=["companies"])


def get_company_service(
    storage: StorageBackend = Depends(get_storage),
    companies: CompanyStorage = Depends(get_company_storage),
) -> CompanyService:
    return CompanyService(storage, companies)


class CompanyCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200)
    industry_sector: str | None = None
    business_description: str | None = None
    country: str | None = None
    city: str | None = None
    status: str = "active"


class CompanyUpdate(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=200)
    trading_name: str | None = None
    legal_name: str | None = None
    industry_sector: str | None = None
    business_description: str | None = None
    country: str | None = None
    city: str | None = None
    website: str | None = None
    status: str | None = None
    notes: str | None = None


class ProjectCreateForCompany(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


@router.get("", response_model=list[CompanySummary])
def list_companies(svc: CompanyService = Depends(get_company_service)):
    svc.migrate_all()  # ensure legacy projects are linked before listing
    return svc.list_summaries()


@router.post("", response_model=Company, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, svc: CompanyService = Depends(get_company_service)):
    return svc.create(Company(**payload.model_dump()))


@router.get("/{company_id}", response_model=Company)
def get_company(company_id: str, svc: CompanyService = Depends(get_company_service)):
    try:
        return svc.get(company_id)
    except NotFoundError:
        raise HTTPException(404, f"Company {company_id!r} not found")


@router.put("/{company_id}", response_model=Company)
def update_company(company_id: str, payload: CompanyUpdate, svc: CompanyService = Depends(get_company_service)):
    try:
        return svc.update(company_id, payload.model_dump(exclude_unset=True))
    except NotFoundError:
        raise HTTPException(404, f"Company {company_id!r} not found")


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: str, delete_projects: bool = False,
                   svc: CompanyService = Depends(get_company_service)):
    svc.delete(company_id, delete_projects=delete_projects)


@router.get("/{company_id}/projects", response_model=list[ProjectSummary])
def list_company_projects(company_id: str, svc: CompanyService = Depends(get_company_service)):
    return svc.list_projects(company_id)


@router.post("/{company_id}/projects", response_model=BusinessPlanProject,
             status_code=status.HTTP_201_CREATED)
def create_company_project(company_id: str, payload: ProjectCreateForCompany,
                           svc: CompanyService = Depends(get_company_service)):
    try:
        return svc.create_project(company_id, payload.name)
    except NotFoundError:
        raise HTTPException(404, f"Company {company_id!r} not found")
