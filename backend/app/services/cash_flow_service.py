"""IFRS Statement of Cash Flows — indirect method.

Built on the same monthly model as the Balance Sheet
(``balance_sheet_service.compute_monthly``), so the closing cash always
reconciles to the Balance Sheet cash line by construction. The operating /
investing / financing decomposition is proven to sum exactly to the period cash
movement.

Annual view SUMS the activity lines over each year (a movement statement),
unlike the Balance Sheet which shows closing balances.
"""
from __future__ import annotations

import calendar
from datetime import date, datetime, timezone

from dateutil.relativedelta import relativedelta

from ..models import BusinessPlanProject
from ..schemas.cash_flow import (
    CashFlowLineItem,
    CashFlowMetadata,
    CashFlowPeriod,
    CashFlowReconciliation,
    CashFlowResponse,
    CashFlowSummary,
    CashFlowTotals,
    CashFlowWarning,
    CashReconciliationResult,
    ReconciliationCheck,
)
from . import balance_sheet_service as bss
from . import income_statement_service as isvc

_delta = bss._delta


def _add(*arrs):
    return [sum(vals) for vals in zip(*arrs)]


def _neg(arr):
    return [-v for v in arr]


def build_cash_flow_periods(project: BusinessPlanProject, view: str):
    from . import projection_period_service as pps
    months = pps.get_monthly_periods(project)
    n = len(months)
    if view == "annual":
        years = n // 12
        periods = []
        for y in range(years):
            first = months[y * 12]
            last = months[min((y + 1) * 12 - 1, n - 1)]
            periods.append(CashFlowPeriod(index=y, label=f"Year {y + 1}", period_type="annual",
                                          start_date=first.start_date, end_date=last.end_date))
        return periods, years, n
    periods = [CashFlowPeriod(index=t, label=months[t].start_date.strftime("%b %Y"), period_type="monthly",
                              start_date=months[t].start_date, end_date=months[t].end_date) for t in range(n)]
    return periods, n, n


def _flow_view(arr, view, years, n):
    if view == "annual":
        return [round(sum(arr[y * 12:(y + 1) * 12]), 2) for y in range(years)]
    return [round(v, 2) for v in arr]


def _opening_closing(cash, view, years, n):
    if view == "annual":
        opening = [round(cash[y * 12 - 1], 2) if y > 0 else 0.0 for y in range(years)]
        closing = [round(cash[min((y + 1) * 12 - 1, n - 1)], 2) for y in range(years)]
    else:
        opening = [round(cash[t - 1], 2) if t > 0 else 0.0 for t in range(n)]
        closing = [round(cash[t], 2) for t in range(n)]
    return opening, closing


def generate_cash_flow_statement(project, scenario="base", view="yearly", method="indirect") -> CashFlowResponse:
    view = "annual" if view in ("annual", "yearly") else "monthly"
    model = bss.compute_monthly(project, scenario)
    M, n = model.M, model.n
    periods, count, _n = build_cash_flow_periods(project, view)
    years = n // 12

    # ---- monthly line arrays (indirect method) ----
    pbt = M["pbt"]; dep = M["dep"]; finance = M["finance"]; eosb_adj = M["eosb_d"]
    op_before_wc = _add(pbt, dep, finance, eosb_adj)

    wc_inventory = _neg(_delta(M["inventory_wc"]))
    wc_receivables = _neg(M["ar_d"])
    wc_prepayments = [0.0] * n  # operating prepayments are nil (deposits sit in investing)
    wc_payables = M["ap_d"]
    wc_accruals = M["accrued_d"]
    wc_deposits = M["dep_liab_d"]
    wc_vat = M["vat_d"]
    wc_total = _add(wc_inventory, wc_receivables, wc_prepayments, wc_payables, wc_accruals, wc_deposits, wc_vat)

    startup_expensed = _neg(M["expensed_startup"])
    cash_gen_ops = _add(op_before_wc, wc_total, startup_expensed)
    tax_paid = [-(M["tax_exp"][t] - M["tax_d"][t]) for t in range(n)]
    net_operating = _add(cash_gen_ops, tax_paid)

    # investing
    ppe_purchase = _neg(M["additions"])
    intangible_purchase = _neg(M["additions_int"])
    startup_inv_d = _delta(M["startup_inv"])
    cap_startup = _neg(_add(startup_inv_d, M["prepay_d"], M["othernca_d"]))
    disposal = [0.0] * n
    net_investing = _add(ppe_purchase, intangible_purchase, cap_startup, disposal)

    # financing
    founder = _delta(M["share_capital"])
    investor = _delta(M["apic"])
    drawdowns = M["loan_drawdown"]
    repayments = _neg(M["loan_principal"])
    interest_paid = _neg(finance)
    grants = [0.0] * n          # recognised as operating other income in the income statement
    dividends = _neg(M["dividends"])
    net_financing = _add(founder, investor, drawdowns, repayments, interest_paid, dividends, grants)

    net_change = _add(net_operating, net_investing, net_financing)
    opening, closing = _opening_closing(M["cash"], view, years, n)

    def L(key, label, arr, **kw):
        vals = _flow_view(arr, view, years, n)
        return CashFlowLineItem(key=key, label=label, classification=kw.pop("cls", "operating"),
                                values_by_period=vals, total=round(sum(vals), 2), **kw)

    rows: list[CashFlowLineItem] = []
    rows.append(CashFlowLineItem(key="op_hdr", label="Cash flows from operating activities", classification="operating", level=0, is_section_header=True))
    rows.append(L("pbt", "Profit / (loss) before tax", pbt, drilldown_available=True))
    rows.append(CashFlowLineItem(key="adj_hdr", label="Adjustments for:", classification="operating", level=0))
    rows.append(L("dep", "Depreciation and amortisation", dep, level=2, drilldown_available=True))
    rows.append(L("finance", "Finance costs", finance, level=2))
    rows.append(L("eosb", "End-of-service benefit provision", eosb_adj, level=2))
    rows.append(L("op_before_wc", "Operating cash flows before working capital changes", op_before_wc, is_subtotal=True))
    rows.append(CashFlowLineItem(key="wc_hdr", label="Changes in working capital:", classification="operating", level=0))
    rows.append(L("wc_inventory", "(Increase) / decrease in inventories", wc_inventory, level=2, drilldown_available=True))
    rows.append(L("wc_receivables", "(Increase) / decrease in trade and other receivables", wc_receivables, level=2, drilldown_available=True))
    rows.append(L("wc_prepayments", "(Increase) / decrease in prepayments and deposits", wc_prepayments, level=2))
    rows.append(L("wc_payables", "Increase / (decrease) in trade and other payables", wc_payables, level=2, drilldown_available=True))
    rows.append(L("wc_accruals", "Increase / (decrease) in accrued expenses", wc_accruals, level=2))
    rows.append(L("wc_deposits", "Increase / (decrease) in customer deposits", wc_deposits, level=2))
    rows.append(L("wc_vat", "Increase / (decrease) in VAT payable / receivable", wc_vat, level=2, drilldown_available=True))
    if sum(startup_expensed) != 0:
        rows.append(L("startup_expensed", "Pre-operating / startup costs paid", startup_expensed))
    rows.append(L("cash_gen_ops", "Cash generated from / (used in) operations", cash_gen_ops, is_subtotal=True))
    rows.append(L("tax_paid", "Income tax paid", tax_paid, drilldown_available=True))
    rows.append(L("net_operating", "Net cash from / (used in) operating activities", net_operating, is_grand_total=True))

    rows.append(CashFlowLineItem(key="inv_hdr", label="Cash flows from investing activities", classification="investing", level=0, is_section_header=True))
    rows.append(L("ppe_purchase", "Purchase of property, plant and equipment", ppe_purchase, cls="investing", drilldown_available=True))
    rows.append(L("intangible_purchase", "Purchase / development of intangible assets", intangible_purchase, cls="investing"))
    rows.append(L("cap_startup", "Capitalized startup costs", cap_startup, cls="investing"))
    rows.append(L("disposal", "Proceeds from disposal of assets", disposal, cls="investing"))
    rows.append(L("net_investing", "Net cash used in investing activities", net_investing, cls="investing", is_grand_total=True))

    rows.append(CashFlowLineItem(key="fin_hdr", label="Cash flows from financing activities", classification="financing", level=0, is_section_header=True))
    rows.append(L("founder", "Proceeds from founder capital", founder, cls="financing"))
    rows.append(L("investor", "Proceeds from investor equity", investor, cls="financing"))
    rows.append(L("drawdowns", "Proceeds from borrowings", drawdowns, cls="financing", drilldown_available=True))
    rows.append(L("repayments", "Repayment of borrowings", repayments, cls="financing", drilldown_available=True))
    rows.append(L("interest_paid", "Interest and finance charges paid", interest_paid, cls="financing"))
    rows.append(L("grants", "Grants received", grants, cls="financing"))
    rows.append(L("dividends", "Dividends paid", dividends, cls="financing"))
    rows.append(L("net_financing", "Net cash from / (used in) financing activities", net_financing, cls="financing", is_grand_total=True))

    rows.append(L("net_change", "Net increase / (decrease) in cash and cash equivalents", net_change, cls="summary", is_subtotal=True))
    rows.append(CashFlowLineItem(key="opening_cash", label="Cash and cash equivalents at beginning of period",
                                 classification="summary", values_by_period=opening, total=0.0, is_subtotal=True))
    rows.append(CashFlowLineItem(key="closing_cash", label="Cash and cash equivalents at end of period",
                                 classification="summary", values_by_period=closing, total=0.0,
                                 is_grand_total=True, drilldown_available=True))

    # cash reconciliation to the balance sheet
    _opening_bs, bs_closing = _opening_closing(M["cash"], view, years, n)
    cf_closing = [round(opening[i] + _flow_view(net_change, view, years, n)[i], 2) for i in range(len(periods))]
    diff = [round(cf_closing[i] - bs_closing[i], 2) for i in range(len(periods))]
    max_diff = max((abs(d) for d in diff), default=0.0)
    recon = CashReconciliationResult(
        closing_cash_cash_flow=cf_closing, cash_balance_sheet=bs_closing, difference=diff,
        max_difference=round(max_diff, 2), status="reconciled" if max_diff <= 1.0 else "not_reconciled",
    )
    rows.append(CashFlowLineItem(key="cash_recon", label="Cash reconciliation to Statement of Financial Position",
                                 classification="summary", values_by_period=diff, total=0.0, is_subtotal=True,
                                 note="Closing cash (CF) - cash (Balance Sheet)"))

    totals = CashFlowTotals(
        net_cash_from_operating_activities=_flow_view(net_operating, view, years, n),
        net_cash_used_in_investing_activities=_flow_view(net_investing, view, years, n),
        net_cash_from_financing_activities=_flow_view(net_financing, view, years, n),
        net_change_in_cash=_flow_view(net_change, view, years, n),
        opening_cash=opening, closing_cash=closing,
    )

    warnings = [CashFlowWarning(code=c, severity=s, message=m) for c, s, m in _cf_warnings(project, model, max_diff)]

    last = periods[-1].end_date if periods else date.today()
    meta = CashFlowMetadata(
        project_id=project.id, project_name=project.name, scenario=scenario,
        scenario_label=model.scen_label, view=view, method=method, currency=model.currency,
        period_caption=f"For the projected period ended {last.day} {last.strftime('%B %Y')}",
        generated_at=datetime.now(timezone.utc),
    )
    return CashFlowResponse(metadata=meta, periods=periods, rows=rows, totals=totals,
                            cash_reconciliation=recon, warnings=warnings)


def _cf_warnings(project, model, max_diff):
    out = []
    M = model.M
    if max_diff > 1.0:
        out.append(("cash_recon", "critical",
                    f"Cash Flow Statement does not reconcile to Balance Sheet cash by {max_diff:,.0f}."))
    if any(c < -1 for c in M["cash"]):
        out.append(("negative_cash", "critical", "Projected closing cash balance is negative."))
    if project.working_capital is None:
        out.append(("no_wc", "warning", "No working capital assumptions — movements use defaults."))
    if project.tax and project.tax.vat_enabled and not project.tax.vat_payment_frequency:
        out.append(("no_vat_freq", "warning", "VAT enabled but payment frequency missing."))
    out.append(("interest_policy", "info", "Interest paid is presented under financing activities (default policy)."))
    return out


def build_summary(project, scenario) -> CashFlowSummary:
    stmt = generate_cash_flow_statement(project, scenario, "annual")
    t = stmt.totals
    op = sum(t.net_cash_from_operating_activities)
    inv = sum(t.net_cash_used_in_investing_activities)
    fin = sum(t.net_cash_from_financing_activities)
    return CashFlowSummary(
        project_id=project.id, scenario=scenario, currency=stmt.metadata.currency,
        net_operating_cash_flow=round(op, 2), net_investing_cash_flow=round(inv, 2),
        net_financing_cash_flow=round(fin, 2), net_change_in_cash=round(op + inv + fin, 2),
        closing_cash=round(t.closing_cash[-1], 2) if t.closing_cash else 0.0,
        free_cash_flow=round(op + inv, 2),  # operating + capex (investing)
        reconciliation_status=stmt.cash_reconciliation.status,
    )


def build_reconciliation(project, scenario) -> CashFlowReconciliation:
    stmt = generate_cash_flow_statement(project, scenario, "annual")
    _ctx, b = isvc._compute(project, scenario)
    model = bss.compute_monthly(project, scenario)
    M = model.M
    checks: list[ReconciliationCheck] = []

    def chk(key, label, passed, sev="warning", detail=None):
        checks.append(ReconciliationCheck(key=key, label=label, passed=passed,
                                          severity="info" if passed else sev, detail=detail))

    row = {r.key: r for r in stmt.rows}
    pbt_cf = sum(row["pbt"].values_by_period)
    chk("pbt", "Profit before tax reconciles to the Income Statement",
        abs(pbt_cf - sum(b["pbt"])) < 1.0, "critical")
    chk("depreciation", "Depreciation add-back reconciles to the Income Statement",
        abs(sum(row["dep"].values_by_period) - sum(b["dep_total"])) < 1.0, "critical")
    chk("finance", "Finance costs reconcile to the Income Statement",
        abs(sum(row["finance"].values_by_period) - sum(b["finance_total"])) < 1.0, "warning")
    chk("capex", "CapEx reconciles to fixed asset additions",
        abs(sum(row["ppe_purchase"].values_by_period) + sum(row["intangible_purchase"].values_by_period)
            + sum(M["additions"]) + sum(M["additions_int"])) < 1.0, "warning")
    chk("drawdowns", "Loan drawdowns reconcile to financing assumptions",
        abs(sum(row["drawdowns"].values_by_period) - sum(loan.amount for loan in project.financing.loans)) < 1.0, "warning")
    chk("equity", "Equity injections reconcile to financing assumptions",
        abs(sum(row["founder"].values_by_period) - project.financing.equity.founder_capital) < 1.0, "critical")
    chk("interest_financing", "Interest paid presented under financing activities",
        abs(sum(row["interest_paid"].values_by_period)) > 0 or sum(b["finance_total"]) == 0, "info")
    chk("cash_recon", "Closing cash reconciles to Balance Sheet cash",
        stmt.cash_reconciliation.status == "reconciled", "critical",
        detail=f"max difference {stmt.cash_reconciliation.max_difference:,.2f}")
    # annual sums monthly check
    monthly = generate_cash_flow_statement(project, scenario, "monthly")
    m_op = sum(next(r for r in monthly.rows if r.key == "net_operating").values_by_period)
    a_op = sum(row["net_operating"].values_by_period)
    chk("annual_sums", "Annual activity lines equal the sum of monthly movements",
        abs(m_op - a_op) < 1.0, "critical")

    return CashFlowReconciliation(
        project_id=project.id, scenario=scenario,
        all_passed=all(c.passed for c in checks if c.severity != "info"),
        checks=checks, warnings=stmt.warnings,
    )


def drilldown(project, scenario, line_item_key, view="annual") -> dict:
    stmt = generate_cash_flow_statement(project, scenario, view)
    for r in stmt.rows:
        if r.key == line_item_key:
            return {"key": r.key, "label": r.label, "periods": [p.label for p in stmt.periods],
                    "values_by_period": r.values_by_period,
                    "children": [{"key": c.key, "label": c.label, "values_by_period": c.values_by_period} for c in r.children]}
    return {"key": line_item_key, "label": line_item_key, "periods": [p.label for p in stmt.periods], "values_by_period": []}
