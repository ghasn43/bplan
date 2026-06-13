"""Tests for the textual business plan module + report integration."""
from __future__ import annotations

import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.reports import ReportRequest
from app.services import pdf_report_service as pdfsvc
from app.services import report_data_service as rd
from app.services import word_report_service as wordsvc
from app.storage import get_storage

PID = "demo_aquapure"
B = f"/api/projects/{PID}/text-plan"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/demo/load-aquapure")
        yield c


@pytest.fixture
def fresh(client):
    """Reset the demo (and its text plan) before tests that mutate it."""
    client.post("/api/demo/load-aquapure")
    return client


def _first_section(client):
    return client.get(B).json()["sections"][0]


# 1. Text plan route returns 200
def test_text_plan_200(client):
    r = client.get(B)
    assert r.status_code == 200
    assert r.json()["sections"]  # demo is seeded


# 2. Section can be created
def test_create_section(fresh):
    r = fresh.post(B + "/sections", json={"title": "New Section", "section_type": "custom"})
    assert r.status_code == 201
    assert r.json()["title"] == "New Section"


# 3. Topic can be created
def test_create_topic(fresh):
    sid = _first_section(fresh)["id"]
    r = fresh.post(B + "/topics", json={"section_id": sid, "title": "New Topic"})
    assert r.status_code == 201
    assert r.json()["section_id"] == sid


# 4. Topic can be updated with rich text (word count computed)
def test_update_topic_richtext(fresh):
    sid = _first_section(fresh)["id"]
    tid = fresh.post(B + "/topics", json={"section_id": sid, "title": "T"}).json()["id"]
    r = fresh.put(B + f"/topics/{tid}", json={"content_html": "<p>Hello <strong>brave</strong> new world</p>"})
    assert r.status_code == 200
    assert r.json()["word_count"] == 4
    assert r.json()["status"] == "draft"


# 5. Section can be deleted
def test_delete_section(fresh):
    sid = fresh.post(B + "/sections", json={"title": "Temp"}).json()["id"]
    assert fresh.delete(B + f"/sections/{sid}").status_code == 204
    assert all(s["id"] != sid for s in fresh.get(B).json()["sections"])


# 6. Topic can be deleted
def test_delete_topic(fresh):
    sid = _first_section(fresh)["id"]
    tid = fresh.post(B + "/topics", json={"section_id": sid, "title": "Temp"}).json()["id"]
    assert fresh.delete(B + f"/topics/{tid}").status_code == 204


# 7. Sections can be reordered
def test_reorder_sections(fresh):
    ids = [s["id"] for s in fresh.get(B).json()["sections"]]
    reversed_ids = list(reversed(ids))
    r = fresh.put(B + "/reorder-sections", json={"ordered_section_ids": reversed_ids})
    assert r.status_code == 200
    assert [s["id"] for s in r.json()["sections"]] == reversed_ids


# 8. Topics can be reordered within a section
def test_reorder_topics(fresh):
    section = _first_section(fresh)
    sid = section["id"]
    tids = [t["id"] for t in section["topics"]]
    rev = list(reversed(tids))
    r = fresh.put(B + "/reorder-topics", json={"section_id": sid, "ordered_topic_ids": rev})
    assert r.status_code == 200
    assert [t["id"] for t in r.json()["topics"]] == rev


# 9. Topic can be moved to another section
def test_move_topic(fresh):
    doc = fresh.get(B).json()
    src, dst = doc["sections"][0], doc["sections"][1]
    tid = src["topics"][0]["id"]
    r = fresh.put(B + "/move-topic", json={"topic_id": tid, "target_section_id": dst["id"], "target_order_index": 0})
    assert r.status_code == 200
    doc2 = fresh.get(B).json()
    dst2 = next(s for s in doc2["sections"] if s["id"] == dst["id"])
    assert dst2["topics"][0]["id"] == tid


# 10. Outline suggestions return a recommended template
def test_outline_suggestions(client):
    r = client.get(B + "/outline-suggestions")
    assert r.status_code == 200
    body = r.json()
    assert body["recommended_template_id"]
    assert len(body["templates"]) >= 6


# 11. Applying a template creates sections and topics
def test_apply_template(fresh):
    r = fresh.post(B + "/apply-outline-template", json={"template_id": "saas", "mode": "replace"})
    assert r.status_code == 200
    assert r.json()["template_id"] == "saas"
    assert len(r.json()["sections"]) >= 10


# 12. AquaPure is detected as the Water Treatment / Environmental template
def test_aquapure_water_treatment(client):
    body = client.get(B + "/outline-suggestions").json()
    assert body["detected_business_type"] == "water_treatment"
    assert body["recommended_template_id"] == "water_treatment"


# 13. Completion calculates correctly
def test_completion(fresh):
    r = fresh.get(B + "/completion")
    assert r.status_code == 200
    body = r.json()
    assert body["section_count"] == 15
    assert body["topic_count"] > 0
    assert 0 <= body["completion_percent"] <= 100
    assert body["word_count"] > 0


# 14. Report context includes the textual business plan
def test_report_context_includes_text_plan(client):
    proj = get_storage().get_project(PID)
    req = ReportRequest(scenario="base", view="yearly", report_style="investor")
    ctx = rd.build_report_context(proj, "base", "yearly", req)
    assert ctx["text_plan"]["has_content"]
    assert ctx["text_plan"]["sections"]


# 15. Word report includes text plan sections
def test_word_includes_text_plan(client):
    proj = get_storage().get_project(PID)
    req = ReportRequest(scenario="base", view="yearly", report_style="investor")
    f = wordsvc.generate_business_plan_docx(proj, req)
    path = rd.report_path(proj.id, f.file_name)
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
    assert "Executive Summary" in xml
    assert "imports, assembles" in xml  # sample narrative content


# 16. PDF report includes text plan sections
def test_pdf_includes_text_plan(client):
    proj = get_storage().get_project(PID)
    req = ReportRequest(scenario="base", view="yearly", report_style="investor")
    html = pdfsvc.render_report_html(rd.build_report_context(proj, "base", "yearly", req))
    assert 'class="richtext"' in html
    assert "imports, assembles" in html


# 17. Excluding the text plan removes it from the report context
def test_exclude_text_plan(client):
    proj = get_storage().get_project(PID)
    req = ReportRequest(scenario="base", view="yearly", include_text_plan=False)
    ctx = rd.build_report_context(proj, "base", "yearly", req)
    assert ctx["text_plan"]["has_content"] is False


# 18. Duplicate section deep-copies topics with fresh ids
def test_duplicate_section(fresh):
    section = _first_section(fresh)
    r = fresh.post(B + f"/sections/{section['id']}/duplicate")
    assert r.status_code == 200
    clone = r.json()
    assert clone["id"] != section["id"]
    assert "(copy)" in clone["title"]
    assert len(clone["topics"]) == len(section["topics"])
    if section["topics"]:
        assert clone["topics"][0]["id"] != section["topics"][0]["id"]
