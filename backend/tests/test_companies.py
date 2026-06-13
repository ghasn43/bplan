"""Tests for the Company entity (parent of projects)."""
from __future__ import annotations

import zipfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.reports import ReportRequest
from app.services import report_data_service as rd
from app.services import word_report_service as wordsvc
from app.storage import get_storage

COMPANY = "AquaPure Smart Filters FZE"
PROJECT = "Dubai Smart Water Filtration Expansion Plan"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def demo(client):
    client.post("/api/demo/load-aquapure")
    return client


def _aquapure(client):
    return next(c for c in client.get("/api/companies").json() if c["company_name"] == COMPANY
                or c["id"] == "company_aquapure")


# 1. Demo creates the AquaPure company with its Dubai project
def test_demo_creates_company_and_project(demo):
    comp = next(c for c in demo.get("/api/companies").json() if c["id"] == "company_aquapure")
    assert comp["company_name"] == COMPANY
    assert comp["status"] == "demo"
    assert comp["total_projects"] >= 1
    projs = demo.get("/api/companies/company_aquapure/projects").json()
    assert any(p["project_name"] == PROJECT for p in projs)
    assert any(p["id"] == "demo_aquapure" for p in projs)


# 2. A company can be created independently
def test_create_company(client):
    r = client.post("/api/companies", json={"company_name": "Standalone Co", "industry_sector": "Retail"})
    assert r.status_code == 201
    assert r.json()["company_name"] == "Standalone Co"
    client.delete(f"/api/companies/{r.json()['id']}")


# 3. A company can have multiple projects
def test_company_multiple_projects(demo):
    demo.post("/api/companies/company_aquapure/projects", json={"name": "Abu Dhabi Commercial Filtration Launch"})
    demo.post("/api/companies/company_aquapure/projects", json={"name": "GCC Distribution Business Plan"})
    comp = next(c for c in demo.get("/api/companies").json() if c["id"] == "company_aquapure")
    assert comp["total_projects"] >= 3


# 4. Company name is editable
def test_company_name_editable(demo):
    r = demo.put("/api/companies/company_aquapure", json={"company_name": "AquaPure Water Technologies FZE"})
    assert r.status_code == 200
    assert r.json()["company_name"] == "AquaPure Water Technologies FZE"


# 5. Editing the company name does not change the project name
def test_company_edit_keeps_project(demo):
    demo.put("/api/companies/company_aquapure", json={"company_name": "Renamed Co FZE"})
    setup = demo.get("/api/projects/demo_aquapure/setup").json()
    assert setup["project_name"] == PROJECT


# 6. Editing the project name does not change the company name
def test_project_edit_keeps_company(demo):
    s = demo.get("/api/projects/demo_aquapure/setup").json()
    s["project_name"] = "Phase 2 Rollout"
    demo.put("/api/projects/demo_aquapure/setup", json=s)
    comp = demo.get("/api/companies/company_aquapure").json()
    assert comp["company_name"] == COMPANY


# 7. Company name persists after reload (re-GET)
def test_company_persists(demo):
    demo.put("/api/companies/company_aquapure", json={"company_name": "Persisted Co FZE"})
    assert demo.get("/api/companies/company_aquapure").json()["company_name"] == "Persisted Co FZE"


# 8. Reports use company name (from the parent Company) + project name separately
def test_report_uses_company_and_project(demo):
    demo.put("/api/companies/company_aquapure", json={"company_name": "AquaPure Reports Co FZE"})
    proj = get_storage().get_project("demo_aquapure")
    ctx = rd.build_report_context(proj, "base", "yearly", ReportRequest())
    assert ctx["meta"]["company"] == "AquaPure Reports Co FZE"   # from Company record
    assert ctx["meta"]["project_name"] == PROJECT                 # from project setup


# 9. Word report shows the parent company name as entity + project as study
def test_word_uses_company_record(demo):
    demo.put("/api/companies/company_aquapure", json={"company_name": "AquaPure Word Co FZE"})
    proj = get_storage().get_project("demo_aquapure")
    f = wordsvc.generate_business_plan_docx(proj, ReportRequest())
    xml = zipfile.ZipFile(rd.report_path("demo_aquapure", f.file_name)).read("word/document.xml").decode("utf-8", "ignore")
    assert "AquaPure Word Co FZE" in xml
    assert PROJECT in xml
    import shutil
    shutil.rmtree("generated_reports/demo_aquapure", ignore_errors=True)


# 10. Project summary carries company_id + per-project metrics
def test_project_summary_metrics(demo):
    summ = next(s for s in demo.get("/api/projects").json() if s["id"] == "demo_aquapure")
    assert summ["company_id"] == "company_aquapure"
    assert summ["products_count"] > 0
    assert summ["total_funding"] > 0


# 11. Migration backfills a company for a legacy project (no company_id)
def test_migration_backfills(client):
    proj = client.post("/api/projects", json={"name": "Legacy Inc Plan"}).json()
    # legacy project has no company_id
    assert proj.get("company_id") in (None, "")
    # listing companies runs migration
    client.get("/api/companies")
    full = client.get(f"/api/projects/{proj['id']}").json()
    assert full["company_id"]  # now linked to a company
    client.delete(f"/api/projects/{proj['id']}")
