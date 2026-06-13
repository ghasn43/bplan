"""Tests: company name and project name are independent identity fields."""
from __future__ import annotations

import zipfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.reports import ReportRequest
from app.services import report_data_service as rd
from app.services import word_report_service as wordsvc
from app.services.completion import build_completion_report
from app.services.demo_builder import build_demo_project
from app.storage import get_storage

PID = "demo_aquapure"
COMPANY = "AquaPure Smart Filters FZE"
PROJECT = "Dubai Smart Water Filtration Expansion Plan"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/demo/load-aquapure")
        yield c


@pytest.fixture
def fresh(client):
    client.post("/api/demo/load-aquapure")
    return client


def _setup(client):
    return client.get(f"/api/projects/{PID}/setup").json()


# 1. Company and project names save separately and round-trip
def test_save_both_independently(fresh):
    s = _setup(fresh)
    s["business_name"] = "New Co Ltd"
    s["project_name"] = "New Expansion Study"
    r = fresh.put(f"/api/projects/{PID}/setup", json=s)
    assert r.status_code == 200
    out = r.json()
    assert out["business_name"] == "New Co Ltd"
    assert out["project_name"] == "New Expansion Study"
    # reload preserves both
    again = _setup(fresh)
    assert again["business_name"] == "New Co Ltd"
    assert again["project_name"] == "New Expansion Study"


# 2. Editing the project name does not change the company name
def test_edit_project_keeps_company(fresh):
    s = _setup(fresh)
    s["project_name"] = "Phase 2 Rollout"
    fresh.put(f"/api/projects/{PID}/setup", json=s)
    out = _setup(fresh)
    assert out["business_name"] == COMPANY
    assert out["project_name"] == "Phase 2 Rollout"


# 3. Editing the company name (rename endpoint) does not change the project name
def test_edit_company_keeps_project(fresh):
    r = fresh.put(f"/api/projects/{PID}/company-name", json={"business_name": "Renamed Co"})
    assert r.status_code == 200
    out = _setup(fresh)
    assert out["business_name"] == "Renamed Co"
    assert out["project_name"] == PROJECT


# 4. Project summary returns both fields independently
def test_summary_has_both(client):
    client.post("/api/demo/load-aquapure")
    summ = next(s for s in client.get("/api/projects").json() if s["id"] == PID)
    assert summ["company_name"] == COMPANY
    assert summ["project_name"] == PROJECT
    assert summ["company_name"] != summ["project_name"]
    assert summ["industry"]
    assert summ["country"]


# 5. Demo preview returns both, no fallback substitution
def test_demo_preview_has_both(client):
    prev = client.get("/api/demo/aquapure-preview").json()
    assert prev["company_name"] == COMPANY
    assert prev["project_name"] == PROJECT
    assert prev["company_name"] != prev["project_name"]


# 6. Report context: company = entity, project = study (not crossed)
def test_report_meta_distinct(client):
    client.post("/api/demo/load-aquapure")
    proj = get_storage().get_project(PID)
    ctx = rd.build_report_context(proj, "base", "yearly", ReportRequest())
    assert ctx["meta"]["company"] == COMPANY
    assert ctx["meta"]["project_name"] == PROJECT


# 7. Income statement header uses company as the reporting entity + project as study
def test_word_statement_headers(client):
    client.post("/api/demo/load-aquapure")
    proj = get_storage().get_project(PID)
    f = wordsvc.generate_business_plan_docx(proj, ReportRequest())
    xml = zipfile.ZipFile(rd.report_path(PID, f.file_name)).read("word/document.xml").decode("utf-8", "ignore")
    assert COMPANY in xml
    assert "Statement of Profit or Loss" in xml
    assert PROJECT in xml  # study reference appears in statement headers
    import shutil
    shutil.rmtree("generated_reports/demo_aquapure", ignore_errors=True)


# 8. Project setup is incomplete when project_name is missing (not copied from company)
def test_completion_requires_project_name():
    project = build_demo_project()
    project.setup.project_name = ""
    report = build_completion_report(project)
    setup_section = next(s for s in report.sections if s.key == "setup")
    assert not setup_section.complete
    assert "project_name" in setup_section.missing_fields


# 9. Missing setup (no company name yet) marks setup incomplete (no cross-copy)
def test_completion_requires_setup():
    project = build_demo_project()
    project.setup = None
    report = build_completion_report(project)
    setup_section = next(s for s in report.sections if s.key == "setup")
    assert not setup_section.complete


# 9b. The full project GET (the workspace header's data source) reflects the
#     saved company name immediately and after reload; project name unchanged.
def test_project_get_reflects_company_edit(fresh):
    s = _setup(fresh)
    s["business_name"] = "AquaPure Water Technologies FZE"
    assert fresh.put(f"/api/projects/{PID}/setup", json=s).status_code == 200
    proj = fresh.get(f"/api/projects/{PID}").json()
    assert proj["setup"]["business_name"] == "AquaPure Water Technologies FZE"
    assert proj["setup"]["project_name"] == PROJECT
    # reload (simulating a browser refresh hitting the API again)
    proj2 = fresh.get(f"/api/projects/{PID}").json()
    assert proj2["setup"]["business_name"] == "AquaPure Water Technologies FZE"


# 10. Demo seed stores distinct, correct values (project_name != company)
def test_demo_seed_values():
    project = build_demo_project()
    assert project.setup.business_name == COMPANY
    assert project.setup.project_name == PROJECT
    assert project.setup.business_name != project.setup.project_name
