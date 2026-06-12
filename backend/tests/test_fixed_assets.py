"""Tests for the Fixed Assets / CapEx module."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_builder import build_demo_project
from app.services import fixed_asset_service as fas
from app.services import income_statement_service as isvc


@pytest.fixture(scope="module")
def project():
    return build_demo_project()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/demo/load-aquapure")
        yield c


# 1. Route returns 200
def test_list_route(client):
    r = client.get("/api/projects/demo_aquapure/fixed-assets")
    assert r.status_code == 200
    assert len(r.json()) >= 6


# 2-4. Create / update / delete
def test_crud(client):
    created = client.post("/api/projects/demo_aquapure/fixed-assets", json={
        "name": "Test Printer", "category": "equipment", "purchase_amount": 5000,
        "purchase_date": "2026-02-01", "useful_life_years": 5, "residual_value": 500,
    })
    assert created.status_code == 201
    aid = created.json()["id"]

    got = client.get(f"/api/projects/demo_aquapure/fixed-assets/{aid}")
    assert got.status_code == 200 and got.json()["name"] == "Test Printer"

    upd = client.put(f"/api/projects/demo_aquapure/fixed-assets/{aid}", json={
        **created.json(), "name": "Test Printer v2", "active": False,
    })
    assert upd.status_code == 200 and upd.json()["name"] == "Test Printer v2"

    dele = client.delete(f"/api/projects/demo_aquapure/fixed-assets/{aid}")
    assert dele.status_code == 204


# 5 & 6. Depreciation schedule + straight-line
def test_depreciation_schedule(client):
    r = client.get("/api/projects/demo_aquapure/fixed-assets/depreciation-schedule?view=annual")
    assert r.status_code == 200
    d = r.json()
    assert len(d["assets"]) >= 6
    assert len(d["periods"]) == 5
    assert d["grand_total_depreciation"] > 0


def test_straight_line(project):
    asset = next(a for a in project.fixed_assets if a.id == "asset_tools")  # 85k, res 5k, 5y
    start, _years, n = __import__("app.services.projection_period_service", fromlist=["x"]).build_projection_periods(project)
    dep = fas.asset_monthly_depreciation(asset, n, start)
    expected_monthly = (85000 - 5000) / (5 * 12)
    assert abs(dep[0] - expected_monthly) < 0.01
    # depreciates for exactly 60 months, total = depreciable amount
    assert abs(sum(dep) - (85000 - 5000)) < 1.0


# 7. NBV never below residual value
def test_nbv_not_below_residual(project):
    start, _years, n = __import__("app.services.projection_period_service", fromlist=["x"]).build_projection_periods(project)
    for asset in project.fixed_assets:
        dep = fas.asset_monthly_depreciation(asset, n, start)
        nbv = asset.purchase_amount - sum(dep)
        assert nbv >= asset.residual_value - 1.0


# 8. Income statement includes depreciation, tying to the schedule
def test_income_statement_includes_depreciation(project):
    stmt = isvc.generate_income_statement(project, "base", "yearly")
    da = next(li for s in stmt.sections if s.key == "operating_expenses"
              for li in s.line_items if li.key == "depreciation_amortisation")
    sched = fas.generate_depreciation_schedule(project, "yearly".replace("yearly", "annual"))
    assert da.total > 0
    assert abs(da.total - sched.grand_total_depreciation) < 5.0


# 9. Demo has at least 6 assets
def test_demo_has_six_assets(project):
    assert len(project.fixed_assets) >= 6


# Summary endpoint
def test_summary_route(client):
    r = client.get("/api/projects/demo_aquapure/fixed-assets/summary")
    assert r.status_code == 200
    d = r.json()
    assert d["active_assets"] >= 6
    assert d["total_asset_cost"] > 0
    assert d["software_intangible_assets"] >= 1


# Validation: residual cannot exceed purchase
def test_residual_validation(client):
    r = client.post("/api/projects/demo_aquapure/fixed-assets", json={
        "name": "Bad Asset", "category": "equipment", "purchase_amount": 1000,
        "purchase_date": "2026-01-01", "residual_value": 5000,
    })
    assert r.status_code in (400, 422, 500)  # rejected by model validator
