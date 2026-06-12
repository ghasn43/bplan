"""Tests for the two-layer projection architecture (setup + schedule grids)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_builder import build_demo_project
from app.services import income_statement_service as isvc
from app.services import revenue_projection_service as rps


@pytest.fixture(scope="module")
def project():
    return build_demo_project()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/demo/load-aquapure")
        yield c


def test_projection_periods(client):
    m = client.get("/api/projects/demo_aquapure/projection-periods?mode=monthly").json()
    a = client.get("/api/projects/demo_aquapure/projection-periods?mode=annual").json()
    assert len(m) == 60 and m[0]["period_label"] == "Jan 2026"
    assert len(a) == 5 and a[0]["period_label"] == "Year 1"


def test_revenue_grid(client):
    g = client.get("/api/projects/demo_aquapure/revenue-projection?mode=monthly").json()
    assert g["section"] == "revenue"
    assert len(g["rows"]) == 6
    assert len(g["periods"]) == 60
    assert g["grand_total"] > 0


def test_annual_aggregates_monthly_grid(client):
    m = client.get("/api/projects/demo_aquapure/revenue-projection?mode=monthly").json()
    a = client.get("/api/projects/demo_aquapure/revenue-projection?mode=annual").json()
    assert abs(m["grand_total"] - a["grand_total"]) < 1.0
    assert len(a["periods"]) == 5


def test_income_statement_reads_revenue_grid(project):
    """Income statement revenue ties to the revenue projection grand total."""
    grid = rps.generate_revenue_grid(project, "monthly")
    stmt = isvc.generate_income_statement(project, "base", "yearly")
    assert abs(grid.grand_total - stmt.totals.total_revenue) < 5.0


def test_editing_cell_changes_income_statement(client):
    before = client.get(
        "/api/projects/demo_aquapure/income-statement?scenario=base&view=yearly"
    ).json()["totals"]["total_revenue"]

    # Find a revenue stream and set Jan 2026 quantity to a large number.
    grid = client.get("/api/projects/demo_aquapure/revenue-projection?mode=monthly").json()
    stream_id = grid["rows"][0]["item_id"]
    r = client.put(
        "/api/projects/demo_aquapure/revenue-projection/cell?mode=monthly",
        json={"item_id": stream_id, "period_index": 0, "quantity": 100000},
    )
    assert r.status_code == 200

    after = client.get(
        "/api/projects/demo_aquapure/income-statement?scenario=base&view=yearly"
    ).json()["totals"]["total_revenue"]
    assert after > before  # the manual projection edit flows into the statement


def test_direct_cost_grid_and_warnings(client):
    g = client.get("/api/projects/demo_aquapure/direct-cost-projection?mode=monthly").json()
    assert len(g["rows"]) == 14
    # unassigned placeholder warning present
    assert any("unassigned" in w.lower() for w in g["warnings"])


def test_apply_growth_helper(client):
    grid = client.get("/api/projects/demo_aquapure/revenue-projection?mode=monthly").json()
    stream_id = grid["rows"][1]["item_id"]
    r = client.post(
        "/api/projects/demo_aquapure/revenue-projection/apply-growth",
        json={"mode": "monthly", "item_id": stream_id, "base_value": 10, "growth_percent": 5, "start_index": 0},
    )
    assert r.status_code == 200
    row = next(x for x in r.json()["rows"] if x["item_id"] == stream_id)
    # value grows period over period (10 then ~10.5 units * price)
    assert row["cells"][1]["quantity"] > row["cells"][0]["quantity"]
