"""Income statement tests against the AquaPure demo company."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.demo_builder import build_demo_project
from app.services import income_statement_service as svc


@pytest.fixture(scope="module")
def project():
    return build_demo_project()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        c.post("/api/demo/load-aquapure")
        yield c


# 1. Route returns 200
def test_route_returns_200(client):
    r = client.get("/api/projects/demo_aquapure/income-statement?scenario=base&view=yearly")
    assert r.status_code == 200
    assert r.json()["metadata"]["statement_title"] == "Statement of Profit or Loss"


# 2. Periods generated correctly
def test_periods_generated(project):
    yearly = svc.generate_income_statement(project, "base", "yearly")
    monthly = svc.generate_income_statement(project, "base", "monthly")
    assert len(yearly.periods) == 5
    assert len(monthly.periods) == 60
    assert monthly.periods[0].label == "Jan 2026"
    assert yearly.periods[0].label == "Year 1"


# 3 & 4. Revenue and cost of sales are positive
def test_revenue_and_cogs_positive(project):
    r = svc.generate_income_statement(project, "base", "yearly")
    assert r.totals.total_revenue > 0
    assert r.totals.total_cost_of_sales > 0


# 5. Gross profit = revenue - cost of sales
def test_gross_profit_reconciles(project):
    r = svc.generate_income_statement(project, "base", "yearly")
    assert abs(r.totals.gross_profit - (r.totals.total_revenue - r.totals.total_cost_of_sales)) < 1.0


# 6. Operating profit reconciles
def test_operating_profit_reconciles(project):
    r = svc.generate_income_statement(project, "base", "yearly")
    expected = r.totals.gross_profit + r.totals.total_other_income - r.totals.total_operating_expenses
    assert abs(r.totals.operating_profit - expected) < 1.0


# 7. Finance costs included when loans exist
def test_finance_costs_present(project):
    assert len(project.financing.loans) > 0
    r = svc.generate_income_statement(project, "base", "yearly")
    assert r.totals.total_finance_costs > 0


# 8. Tax is calculated when profit before tax is positive
def test_tax_calculated_on_positive_pbt(project):
    pbt = [100000.0] * project.setup.projection_period.years * 12  # always profitable
    ctx = svc.Ctx(project=project, scen=svc._scenario_adj(project, "base"),
                  n=len(pbt), start=project.setup.projection_start_date,
                  years=project.setup.projection_period.years)
    tax = svc.calculate_tax(ctx, pbt)
    assert sum(tax) > 0
    expected = sum(pbt) * (project.tax.corporate_tax_rate / 100.0)
    assert abs(sum(tax) - expected) < 1.0


# 9. Net profit = profit before tax - tax
def test_net_profit_reconciles(project):
    r = svc.generate_income_statement(project, "base", "yearly")
    assert abs(r.totals.profit_for_period - (r.totals.profit_before_tax - r.totals.income_tax_expense)) < 1.0


# 10. Yearly view aggregates monthly view correctly
def test_yearly_aggregates_monthly(project):
    yearly = svc.generate_income_statement(project, "base", "yearly")
    monthly = svc.generate_income_statement(project, "base", "monthly")
    assert abs(yearly.totals.total_revenue - monthly.totals.total_revenue) < 1.0
    assert abs(yearly.totals.profit_for_period - monthly.totals.profit_for_period) < 1.0


# 11. Scenario adjustments change results
def test_scenarios_differ(project):
    base = svc.generate_income_statement(project, "base", "yearly").totals.total_revenue
    cons = svc.generate_income_statement(project, "conservative", "yearly").totals.total_revenue
    opt = svc.generate_income_statement(project, "optimistic", "yearly").totals.total_revenue
    assert base != cons and base != opt


# 12 & 13. Conservative < base < optimistic revenue
def test_scenario_ordering(project):
    base = svc.generate_income_statement(project, "base", "yearly").totals.total_revenue
    cons = svc.generate_income_statement(project, "conservative", "yearly").totals.total_revenue
    opt = svc.generate_income_statement(project, "optimistic", "yearly").totals.total_revenue
    assert cons < base < opt


# 14. Unassigned direct cost produces a warning
def test_unassigned_direct_cost_warning(project):
    r = svc.generate_income_statement(project, "base", "yearly")
    assert any(w.code == "unassigned_direct_cost" for w in r.warnings)
    rec = svc.build_reconciliation(project, "base")
    assert any(c.key == "unassigned_identified" for c in rec.checks)


# Bonus: grant recognised only in optimistic scenario
def test_grant_optimistic_only(project):
    base = svc.generate_income_statement(project, "base", "yearly")
    opt = svc.generate_income_statement(project, "optimistic", "yearly")
    assert base.totals.total_other_income == 0
    assert opt.totals.total_other_income == 100000


# Summary + reconciliation endpoints
def test_summary_and_reconciliation_routes(client):
    s = client.get("/api/projects/demo_aquapure/income-statement/summary?scenario=base")
    assert s.status_code == 200 and "gross_margin" in s.json()
    rec = client.get("/api/projects/demo_aquapure/income-statement/reconciliation?scenario=base")
    assert rec.status_code == 200
    assert rec.json()["all_passed"] is True
