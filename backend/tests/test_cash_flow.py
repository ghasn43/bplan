"""Tests for the Statement of Cash Flows (indirect method)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_builder import build_demo_project
from app.services import cash_flow_service as cfs
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
    r = client.get("/api/projects/demo_aquapure/cash-flow?scenario=base&view=yearly")
    assert r.status_code == 200
    assert r.json()["metadata"]["statement_title"] == "Statement of Cash Flows"


# 2 & 3. Period counts
def test_period_counts(project):
    annual = cfs.generate_cash_flow_statement(project, "base", "annual")
    monthly = cfs.generate_cash_flow_statement(project, "base", "monthly")
    assert len(annual.periods) == 5
    assert len(monthly.periods) == 60


# 4. Indirect method
def test_method_indirect(project):
    assert cfs.generate_cash_flow_statement(project, "base", "annual").metadata.method == "indirect"


# 5. PBT equals income statement PBT
def test_pbt_matches_income_statement(project):
    cf = cfs.generate_cash_flow_statement(project, "base", "annual")
    _ctx, b = isvc._compute(project, "base")
    assert abs(sum(_row(cf, "pbt").values_by_period) - sum(b["pbt"])) < 1.0


# 6. Depreciation add-back equals income statement D&A
def test_depreciation_addback(project):
    cf = cfs.generate_cash_flow_statement(project, "base", "annual")
    _ctx, b = isvc._compute(project, "base")
    assert abs(sum(_row(cf, "dep").values_by_period) - sum(b["dep_total"])) < 1.0


# 7. Working capital movements present
def test_working_capital_movements(project):
    cf = cfs.generate_cash_flow_statement(project, "base", "annual")
    assert _row(cf, "wc_receivables").values_by_period  # exists
    assert _row(cf, "wc_payables").values_by_period


# 8. CapEx in investing
def test_capex_in_investing(project):
    cf = cfs.generate_cash_flow_statement(project, "base", "annual")
    assert _row(cf, "ppe_purchase").values_by_period[0] < 0  # year 1 outflow


# 9 & 10 & 11 & 12. Financing lines present
def test_financing_lines(project):
    cf = cfs.generate_cash_flow_statement(project, "base", "annual")
    assert _row(cf, "drawdowns").values_by_period[0] > 0          # loan drawdowns
    assert _row(cf, "repayments").values_by_period[1] < 0         # repayments (after grace)
    assert _row(cf, "founder").values_by_period[0] == project.financing.equity.founder_capital
    assert _row(cf, "interest_paid").values_by_period[0] <= 0     # interest in financing


# 13. Net change reconciles opening/closing
def test_net_change_rolls_forward(project):
    cf = cfs.generate_cash_flow_statement(project, "base", "annual")
    opening = cf.totals.opening_cash
    closing = cf.totals.closing_cash
    change = cf.totals.net_change_in_cash
    for i in range(len(closing)):
        assert abs((opening[i] + change[i]) - closing[i]) < 1.0


# 14. Closing cash reconciles to balance sheet cash
def test_closing_cash_matches_balance_sheet(project):
    cf = cfs.generate_cash_flow_statement(project, "base", "annual")
    bs = bss.generate_balance_sheet(project, "base", "annual")
    bs_cash = next(r for r in bs.rows if r.key == "cash").values_by_period
    assert cf.cash_reconciliation.status == "reconciled"
    for i in range(5):
        assert abs(cf.totals.closing_cash[i] - bs_cash[i]) < 1.0


# 15. Annual activity == sum of monthly
def test_annual_sums_monthly(project):
    annual = cfs.generate_cash_flow_statement(project, "base", "annual")
    monthly = cfs.generate_cash_flow_statement(project, "base", "monthly")
    a_op = sum(_row(annual, "net_operating").values_by_period)
    m_op = sum(_row(monthly, "net_operating").values_by_period)
    assert abs(a_op - m_op) < 1.0


# 16. Annual ending cash == year-end balance sheet cash
def test_annual_ending_cash(project):
    cf = cfs.generate_cash_flow_statement(project, "base", "annual")
    bs = bss.generate_balance_sheet(project, "base", "annual")
    bs_cash = next(r for r in bs.rows if r.key == "cash").values_by_period
    assert abs(cf.totals.closing_cash[-1] - bs_cash[-1]) < 1.0


# 17. Scenarios differ
def test_scenarios_differ(project):
    base = cfs.generate_cash_flow_statement(project, "base", "annual")
    opt = cfs.generate_cash_flow_statement(project, "optimistic", "annual")
    assert _row(base, "net_operating").values_by_period[-1] != _row(opt, "net_operating").values_by_period[-1]


# 18. Summary + reconciliation endpoints
def test_summary_and_reconciliation(client):
    s = client.get("/api/projects/demo_aquapure/cash-flow/summary?scenario=base")
    assert s.status_code == 200 and "free_cash_flow" in s.json()
    rec = client.get("/api/projects/demo_aquapure/cash-flow/reconciliation?scenario=base")
    assert rec.status_code == 200
    assert any(c["key"] == "cash_recon" and c["passed"] for c in rec.json()["checks"])
    drill = client.get("/api/projects/demo_aquapure/cash-flow/drilldown/net_operating?scenario=base")
    assert drill.status_code == 200
