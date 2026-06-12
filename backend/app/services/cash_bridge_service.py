"""Internal cash-bridge service.

A preliminary, internal cash-movement calculation used by the Balance Sheet to
present how the closing cash balance is derived. It delegates to the balance
sheet engine (the single source of truth for positions) so the bridge always
reconciles to the balance sheet's cash line. This will graduate into the full
Cash Flow Statement module in a later phase.
"""
from __future__ import annotations

from ..models import BusinessPlanProject
from . import balance_sheet_service as bss


def generate_cash_bridge(project: BusinessPlanProject, scenario: str, view: str = "annual") -> dict:
    return bss.cash_bridge_drilldown(project, scenario, view)


def _model(project: BusinessPlanProject, scenario: str):
    return bss.compute_monthly(project, scenario).M


def calculate_cash_collections(project, scenario):       # net profit proxy + Δreceivables handled in bridge
    return _model(project, scenario)["net"]


def calculate_loan_drawdowns(project, scenario):
    return _model(project, scenario)["loan_drawdown"]


def calculate_loan_principal_repayments(project, scenario):
    return _model(project, scenario)["loan_principal"]


def calculate_equity_injections(project, scenario):
    return _model(project, scenario)["equity_inject"]


def calculate_capex_payments(project, scenario):
    M = _model(project, scenario)
    return [a + b for a, b in zip(M["additions"], M["additions_int"])]


def calculate_startup_cost_payments(project, scenario):
    return _model(project, scenario)["expensed_startup"]


def calculate_closing_cash(project, scenario):
    return _model(project, scenario)["cash"]
