"""Tests for the Statement of Financial Position (Balance Sheet)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_builder import build_demo_project
from app.services import balance_sheet_service as bss
from app.services import income_statement_service as isvc


@pytest.fixture(scope="module")
def project():
    return build_demo_project()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/demo/load-aquapure")
        yield c


def _row(stmt, key):
    return next(r for r in stmt.rows if r.key == key)


# 1. Route returns 200
def test_route_200(client):
    r = client.get("/api/projects/demo_aquapure/balance-sheet?scenario=base&view=yearly")
    assert r.status_code == 200
    assert r.json()["metadata"]["statement_title"] == "Statement of Financial Position"


# 2 & 3. Period counts
def test_period_counts(project):
    annual = bss.generate_balance_sheet(project, "base", "annual")
    monthly = bss.generate_balance_sheet(project, "base", "monthly")
    assert len(annual.periods) == 5
    assert len(monthly.periods) == 60


# 4. Total assets calculated
def test_total_assets(project):
    s = bss.generate_balance_sheet(project, "base", "annual")
    assert len(_row(s, "total_assets").values_by_period) == 5


# 5 & 6. PPE and intangibles positive when assets exist
def test_ppe_and_intangibles(project):
    s = bss.generate_balance_sheet(project, "base", "annual")
    assert _row(s, "ppe").values_by_period[0] > 0
    assert _row(s, "intangibles").values_by_period[0] > 0


# 7. Receivables from revenue and collection days
def test_receivables(project):
    s = bss.generate_balance_sheet(project, "base", "annual")
    assert all(v >= 0 for v in _row(s, "receivables").values_by_period)
    assert _row(s, "receivables").values_by_period[-1] > 0


# 8. Inventory from cost of sales and inventory days
def test_inventory(project):
    s = bss.generate_balance_sheet(project, "base", "annual")
    assert _row(s, "inventory").values_by_period[-1] > 0


# 9. Borrowings from loan assumptions
def test_borrowings(project):
    s = bss.generate_balance_sheet(project, "base", "annual")
    # current portion + long-term should be positive early in the plan
    lt = _row(s, "lt_borrowings").values_by_period[0]
    cur = _row(s, "cpltd").values_by_period[0]
    assert lt + cur > 0


# 10. Equity includes founder + investor capital
def test_equity_capital(project):
    s = bss.generate_balance_sheet(project, "base", "annual")
    assert _row(s, "share_capital").values_by_period[0] == project.financing.equity.founder_capital
    assert _row(s, "apic").values_by_period[0] == project.financing.equity.investor_equity


# 11. Retained earnings reconcile to cumulative net profit (less expensed startup)
def test_retained_earnings_reconcile(project):
    s = bss.generate_balance_sheet(project, "base", "annual")
    _ctx, b = isvc._compute(project, "base")
    cum_net = sum(b["net"])
    exp_startup = sum(sc.amount for sc in project.startup_costs if not sc.capitalized)
    assert abs(_row(s, "retained").values_by_period[-1] - (cum_net - exp_startup)) < 1.0


# 12. Annual balance sheet uses closing balances, not summed months
def test_annual_uses_closing_not_sum(project):
    annual = bss.generate_balance_sheet(project, "base", "annual")
    monthly = bss.generate_balance_sheet(project, "base", "monthly")
    # Year 1 PPE == month 12 (index 11) PPE, and != sum of 12 months
    y1_ppe = _row(annual, "ppe").values_by_period[0]
    m12_ppe = _row(monthly, "ppe").values_by_period[11]
    sum12 = sum(_row(monthly, "ppe").values_by_period[0:12])
    assert abs(y1_ppe - m12_ppe) < 1.0
    assert abs(y1_ppe - sum12) > 1.0


# 13. Balance check within tolerance
def test_balanced(project):
    for sc in ("base", "conservative", "optimistic"):
        s = bss.generate_balance_sheet(project, sc, "annual")
        assert s.balance_check.status == "balanced"
        assert s.balance_check.max_difference <= 1.0


# 14. Negative cash warning appears (the demo is underfunded)
def test_negative_cash_warning(project):
    s = bss.generate_balance_sheet(project, "base", "annual")
    assert any(w.code == "negative_cash" for w in s.warnings)


# 15. Scenario changes the values
def test_scenarios_differ(project):
    base = bss.generate_balance_sheet(project, "base", "annual")
    opt = bss.generate_balance_sheet(project, "optimistic", "annual")
    assert _row(base, "receivables").values_by_period[-1] != _row(opt, "receivables").values_by_period[-1]


# 16. Loads without crashing + summary/reconciliation endpoints
def test_summary_and_reconciliation(client):
    s = client.get("/api/projects/demo_aquapure/balance-sheet/summary?scenario=base")
    assert s.status_code == 200 and "current_ratio" in s.json()
    rec = client.get("/api/projects/demo_aquapure/balance-sheet/reconciliation?scenario=base")
    assert rec.status_code == 200
    # the 'balanced' check must pass
    assert any(c["key"] == "balanced" and c["passed"] for c in rec.json()["checks"])
    drill = client.get("/api/projects/demo_aquapure/balance-sheet/drilldown/cash?scenario=base")
    assert drill.status_code == 200 and "closing_cash" in drill.json()
