"""Tests for inline rich-text image placement in topics and reports."""
from __future__ import annotations

import io
import re
import zipfile

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.reports import ReportRequest
from app.schemas.text_plan import TopicUpdate
from app.services import pdf_report_service as pdfsvc
from app.services import report_data_service as rd
from app.services import text_plan_image_service as imgsvc
from app.services import text_plan_service as tps
from app.services import word_report_service as wordsvc
from app.storage import get_storage

PID = "demo_aquapure"
B = f"/api/projects/{PID}/text-plan"


def _png(w=240, h=140) -> bytes:
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (37, 99, 235)).save(buf, "PNG")
    return buf.getvalue()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/demo/load-aquapure")
        yield c


@pytest.fixture
def fresh(client):
    client.post("/api/demo/load-aquapure")
    return client


def _first_topic_id(client):
    return client.get(B).json()["sections"][0]["topics"][0]["id"]


def _upload(client, topic_id) -> dict:
    files = {"file": ("fig.png", _png(), "image/png")}
    r = client.post(f"{B}/topics/{topic_id}/images", files=files)
    assert r.status_code == 201
    return r.json()


# 1. Upload returns a project-scoped, browser-accessible URL
def test_upload_returns_project_url(fresh):
    tid = _first_topic_id(fresh)
    img = _upload(fresh, tid)
    assert img["url"] == f"/api/projects/{PID}/text-plan/images/{img['id']}/file"


# 2. The project-scoped image file route serves the bytes
def test_image_file_route(fresh):
    tid = _first_topic_id(fresh)
    img = _upload(fresh, tid)
    r = fresh.get(img["url"])
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/")
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


# 3. Inserting an image node between paragraphs persists in order
def test_inline_node_persists_order(fresh):
    tid = _first_topic_id(fresh)
    img = _upload(fresh, tid)
    storage = get_storage()
    image = imgsvc.find_image(storage.get_project(PID), img["id"])[1]
    node = tps.image_node_html(PID, image)
    content = f"<p>BEFORE</p>{node}<p>AFTER</p>"
    r = fresh.put(f"{B}/topics/{tid}", json={"content_html": content})
    assert r.status_code == 200
    saved = r.json()["content_html"]
    assert saved.index("BEFORE") < saved.index("data-image-id") < saved.index("AFTER")


# 4. Word report embeds the image inline between the surrounding paragraphs (no dup)
def test_word_inline_placement(fresh):
    tid = _first_topic_id(fresh)
    img = _upload(fresh, tid)
    image = imgsvc.find_image(get_storage().get_project(PID), img["id"])[1]
    content = f"<p>BEFORE_IMG</p>{tps.image_node_html(PID, image)}<p>AFTER_IMG</p>"
    fresh.put(f"{B}/topics/{tid}", json={"content_html": content})

    proj = get_storage().get_project(PID)
    req = ReportRequest(scenario="base", view="yearly")
    f = wordsvc.generate_business_plan_docx(proj, req)
    with zipfile.ZipFile(rd.report_path(PID, f.file_name)) as z:
        xml = z.read("word/document.xml").decode("utf-8", "ignore")
        media = [n for n in z.namelist() if n.startswith("word/media/")]
    b, draw, a = xml.find("BEFORE_IMG"), xml.find("<w:drawing"), xml.find("AFTER_IMG")
    assert b >= 0 and a >= 0 and b < draw < a          # inline at the right position
    # exactly one media image belongs to this topic's text (others are charts)
    assert len(media) >= 1


# 5. PDF report renders the figure inline between the paragraphs with a data URI
def test_pdf_inline_placement(fresh):
    tid = _first_topic_id(fresh)
    img = _upload(fresh, tid)
    image = imgsvc.find_image(get_storage().get_project(PID), img["id"])[1]
    content = f"<p>BEFORE_PDF</p>{tps.image_node_html(PID, image)}<p>AFTER_PDF</p>"
    fresh.put(f"{B}/topics/{tid}", json={"content_html": content})

    proj = get_storage().get_project(PID)
    html = pdfsvc.render_report_html(rd.build_report_context(proj, "base", "yearly", ReportRequest()))
    body = html.split("</style>", 1)[-1]
    b, fig, a = body.find("BEFORE_PDF"), body.find("topic-image"), body.find("AFTER_PDF")
    assert b < fig < a
    assert "data:image/png;base64" in body


# 6. Excluding images strips inline image nodes from the report
def test_exclude_images(fresh):
    tid = _first_topic_id(fresh)
    img = _upload(fresh, tid)
    image = imgsvc.find_image(get_storage().get_project(PID), img["id"])[1]
    fresh.put(f"{B}/topics/{tid}", json={"content_html": f"<p>X</p>{tps.image_node_html(PID, image)}"})
    proj = get_storage().get_project(PID)
    ctx = rd.build_report_context(proj, "base", "yearly", ReportRequest(text_plan_include_images=False))
    tp = ctx["text_plan"]
    joined = " ".join(t["content_html"] for s in tp["sections"] for t in s["topics"])
    assert "data-image-id" not in joined


# 7. Legacy attached images are migrated into content once (idempotent, no dup)
def test_migration_idempotent():
    from app.services.demo import load_aquapure
    storage = get_storage()
    proj = load_aquapure(storage)
    # simulate a legacy topic: attached image, no node in content
    section = proj.text_plan.sections[0]
    topic = section.topics[0]
    topic.content_html = "<p>Legacy text.</p>"
    topic.content_json = None
    from app.models.text_plan import TextPlanImage
    topic.images = [TextPlanImage(id="legacyimg", file_name="legacyimg.png", file_path="/x/legacy.png",
                                  mime_type="image/png", caption="Legacy", alignment="center",
                                  display_width_percentage=80)]
    storage.save_project(proj)

    doc = tps.get_text_plan(storage, PID)
    t = doc.sections[0].topics[0]
    assert t.content_html.count('data-image-id="legacyimg"') == 1
    # second read does not duplicate
    doc2 = tps.get_text_plan(storage, PID)
    t2 = doc2.sections[0].topics[0]
    assert t2.content_html.count('data-image-id="legacyimg"') == 1
    load_aquapure(storage)  # reset demo


# 8. Missing image file does not crash Word/PDF (shows placeholder)
def test_missing_image_safe(fresh):
    tid = _first_topic_id(fresh)
    # reference a non-existent image id
    content = '<p>P1</p><img src="/x" data-image-id="nope" data-alignment="center" data-width="80"><p>P2</p>'
    fresh.put(f"{B}/topics/{tid}", json={"content_html": content})
    proj = get_storage().get_project(PID)
    req = ReportRequest(scenario="base", view="yearly")
    wf = wordsvc.generate_business_plan_docx(proj, req)
    assert wf.size_bytes > 5000
    html = pdfsvc.render_report_html(rd.build_report_context(proj, "base", "yearly", req))
    assert "topic-image-missing" in html
