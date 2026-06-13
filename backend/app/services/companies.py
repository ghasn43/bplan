"""Company service: company CRUD, project linkage, and legacy migration.

A company is the parent of one or more :class:`BusinessPlanProject` records
(linked via ``project.company_id``). The company name lives once at company
level; projects keep their own ``setup.project_name``.
"""
from __future__ import annotations

from ..models import BusinessPlanProject, Company, CompanySummary
from ..storage.base import NotFoundError, StorageBackend
from ..storage.company_storage import CompanyStorage
from ..utils.ids import utcnow
from .completion import build_completion_report

PROFILE_FIELDS = ("company_name", "industry_sector", "country", "city", "business_description")


class CompanyService:
    def __init__(self, storage: StorageBackend, companies: CompanyStorage) -> None:
        self.storage = storage
        self.companies = companies

    # -- helpers ----------------------------------------------------------
    def _profile_completion(self, company: Company) -> int:
        filled = sum(1 for f in PROFILE_FIELDS if (getattr(company, f, None) or "").strip())
        return round(100 * filled / len(PROFILE_FIELDS))

    def _project_status(self, project: BusinessPlanProject) -> str:
        pct = build_completion_report(project).completion_percent
        return "active" if pct >= 100 else "draft"

    def _summary(self, company: Company, projects: list[BusinessPlanProject]) -> CompanySummary:
        owned = [p for p in projects if p.company_id == company.id]
        statuses = [self._project_status(p) for p in owned]
        return CompanySummary(
            id=company.id, created_at=company.created_at, updated_at=company.updated_at,
            company_name=company.company_name, industry_sector=company.industry_sector,
            country=company.country, city=company.city,
            business_description=company.business_description, status=company.status,
            total_projects=len(owned),
            active_projects=sum(1 for s in statuses if s == "active"),
            draft_projects=sum(1 for s in statuses if s == "draft"),
            profile_completion_percent=self._profile_completion(company),
        )

    # -- CRUD -------------------------------------------------------------
    def list_summaries(self) -> list[CompanySummary]:
        projects = self.storage.list_projects()
        return [self._summary(c, projects) for c in self.companies.list_companies()]

    def get(self, company_id: str) -> Company:
        return self.companies.get_company(company_id)

    def create(self, company: Company) -> Company:
        return self.companies.save_company(company)

    def update(self, company_id: str, patch: dict) -> Company:
        company = self.companies.get_company(company_id)
        for k, v in patch.items():
            if v is not None and hasattr(company, k):
                setattr(company, k, v)
        company.updated_at = utcnow()
        return self.companies.save_company(company)

    def delete(self, company_id: str, *, delete_projects: bool = False) -> None:
        if delete_projects:
            for p in self.storage.list_projects():
                if p.company_id == company_id:
                    self.storage.delete_project(p.id)
        else:
            for p in self.storage.list_projects():
                if p.company_id == company_id:
                    p.company_id = None
                    self.storage.save_project(p)
        self.companies.delete_company(company_id)

    # -- projects of a company -------------------------------------------
    def list_projects(self, company_id: str):
        from .projects import ProjectService
        svc = ProjectService(self.storage)
        return [s for s in svc.list_summaries() if s.company_id == company_id]

    def create_project(self, company_id: str, name: str) -> BusinessPlanProject:
        self.companies.get_company(company_id)  # 404 if missing
        project = BusinessPlanProject(name=name, company_id=company_id)
        return self.storage.save_project(project)

    # -- migration --------------------------------------------------------
    def ensure_company_for_project(self, project: BusinessPlanProject) -> Company:
        """Link a project to a company, creating one from its setup if needed."""
        if project.company_id and self.companies.exists(project.company_id):
            return self.companies.get_company(project.company_id)
        setup = project.setup
        name = (setup.business_name if setup and setup.business_name else project.name).strip()
        existing = next(
            (c for c in self.companies.list_companies() if c.company_name.strip().lower() == name.lower()),
            None,
        )
        if existing:
            company = existing
        else:
            company = Company(
                company_name=name,
                industry_sector=setup.industry if setup else None,
                business_description=setup.business_description if setup else None,
                country=setup.country if setup else None,
                city=setup.city if setup else None,
                status="active",
            )
            self.companies.save_company(company)
        project.company_id = company.id
        self.storage.save_project(project)
        return company

    def migrate_all(self) -> int:
        """Backfill company_id for every legacy project. Returns # linked."""
        count = 0
        for project in self.storage.list_projects():
            if project.company_id and self.companies.exists(project.company_id):
                continue
            self.ensure_company_for_project(project)
            count += 1
        return count

    def company_name_for_project(self, project: BusinessPlanProject) -> str | None:
        """Canonical company name for reports: parent company, else setup."""
        if project.company_id and self.companies.exists(project.company_id):
            return self.companies.get_company(project.company_id).company_name
        if project.setup and project.setup.business_name:
            return project.setup.business_name
        return project.name


def company_service() -> CompanyService:
    from ..storage import get_company_storage, get_storage
    return CompanyService(get_storage(), get_company_storage())
