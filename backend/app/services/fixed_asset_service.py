"""Fixed-asset depreciation service.

Single source of truth for depreciation: the schedule shown on the CapEx page
and the depreciation & amortisation line in the income statement both come from
``asset_monthly_depreciation`` here, so they always agree.
"""
from __future__ import annotations

from datetime import date

from ..models import BusinessPlanProject
from ..models.enums import DepreciationMethod
from ..schemas.fixed_assets import (
    DepreciationAssetRow,
    DepreciationPeriod,
    DepreciationRollforward,
    DepreciationSchedule,
    FixedAssetSummary,
)
from . import projection_period_service as pps

# IFRS-style depreciation line label per asset category.
CATEGORY_DEP_LABEL = {
    "equipment": "Depreciation of equipment",
    "machinery": "Depreciation of equipment",
    "vehicle": "Depreciation of vehicles",
    "furniture": "Depreciation of furniture and fit-out",
    "office_fit_out": "Depreciation of furniture and fit-out",
    "computers": "Depreciation of computers",
    "software_development": "Amortisation of software development",
    "leasehold_improvements": "Depreciation of leasehold improvements",
}
DEFAULT_DEP_LABEL = "Depreciation of other assets"


def _mb(start: date, other: date) -> int:
    return (other.year - start.year) * 12 + (other.month - start.month)


def _zeros(n: int) -> list[float]:
    return [0.0] * n


def asset_monthly_depreciation(asset, n: int, start: date) -> list[float]:
    """Straight-line monthly depreciation from the ready-for-use (or purchase) month.

    Reducing-balance falls back to straight-line in this first version.
    """
    arr = _zeros(n)
    if asset.depreciation_method == DepreciationMethod.NONE or asset.useful_life_years <= 0:
        return arr
    begin = asset.depreciation_start or start
    p_idx = max(0, _mb(start, begin))
    life_months = int(round(asset.useful_life_years * 12))
    if life_months <= 0:
        return arr
    monthly = (asset.purchase_amount - asset.residual_value) / life_months
    for k in range(life_months):
        t = p_idx + k
        if 0 <= t < n:
            arr[t] = monthly
    return arr


def _asset_additions(asset, n: int, start: date) -> list[float]:
    """The asset cost is recognised in the period it is acquired."""
    arr = _zeros(n)
    when = asset.purchase_date or asset.depreciation_start or start
    idx = _mb(start, when)
    if 0 <= idx < n:
        arr[idx] = asset.purchase_amount
    elif idx < 0:
        arr[0] = asset.purchase_amount  # acquired before the projection starts
    return arr


def depreciation_by_category(project: BusinessPlanProject, n: int, start: date):
    """Return (dict[label -> monthly array], list[(asset, monthly array)])."""
    by_label: dict[str, list[float]] = {}
    per_asset: list[tuple[object, list[float]]] = []
    for asset in project.fixed_assets:
        if not getattr(asset, "active", True):
            continue
        arr = asset_monthly_depreciation(asset, n, start)
        per_asset.append((asset, arr))
        label = CATEGORY_DEP_LABEL.get(asset.category.value, DEFAULT_DEP_LABEL)
        by_label.setdefault(label, _zeros(n))
        by_label[label] = [a + b for a, b in zip(by_label[label], arr)]
    return by_label, per_asset


# --------------------------------------------------------------------------
# Depreciation schedule (Tab 2)
# --------------------------------------------------------------------------
def _ranges(view: str, years: int, n: int) -> list[range]:
    if view == "annual":
        return [range(y * 12, min(n, (y + 1) * 12)) for y in range(years)]
    return [range(t, t + 1) for t in range(n)]


def generate_depreciation_schedule(project: BusinessPlanProject, view: str) -> DepreciationSchedule:
    start, years, n = pps.build_projection_periods(project)
    plist_src = pps.get_annual_periods(project) if view == "annual" else pps.get_monthly_periods(project)
    periods = [
        DepreciationPeriod(index=p.period_index, label=p.period_label, period_type=p.period_type,
                           start_date=p.start_date, end_date=p.end_date)
        for p in plist_src
    ]
    ranges = _ranges(view, years, n)
    currency = project.setup.currency if project.setup else "USD"
    warnings: list[str] = []

    # Aggregate monthly series
    add_m = _zeros(n)
    dep_m = _zeros(n)
    asset_rows: list[DepreciationAssetRow] = []

    for asset in project.fixed_assets:
        if not getattr(asset, "active", True):
            continue
        if asset.depreciation_method == DepreciationMethod.REDUCING_BALANCE:
            warnings.append(f"Asset '{asset.name}' uses reducing balance; straight-line applied in this version.")
        dep = asset_monthly_depreciation(asset, n, start)
        adds = _asset_additions(asset, n, start)
        add_m = [a + b for a, b in zip(add_m, adds)]
        dep_m = [a + b for a, b in zip(dep_m, dep)]

        dep_periods = [round(sum(dep[t] for t in r), 2) for r in ranges]
        cum_add = sum(adds)
        cum_dep = sum(dep)
        asset_rows.append(DepreciationAssetRow(
            asset_id=asset.id, label=asset.name, category=asset.category.value,
            category_label=CATEGORY_DEP_LABEL.get(asset.category.value, DEFAULT_DEP_LABEL),
            depreciation_by_period=dep_periods, total_depreciation=round(cum_dep, 2),
            closing_net_book_value=round(cum_add - cum_dep, 2),
        ))

    # Cumulative monthly series for the roll-forward
    cum_add_m = []
    cum_dep_m = []
    ra = da = 0.0
    for t in range(n):
        ra += add_m[t]; da += dep_m[t]
        cum_add_m.append(ra); cum_dep_m.append(da)

    roll = DepreciationRollforward()
    totals_by_period: list[float] = []
    for r in ranges:
        s, e = r.start, r.stop - 1
        opening_cost = cum_add_m[s - 1] if s > 0 else 0.0
        additions = sum(add_m[t] for t in r)
        charge = sum(dep_m[t] for t in r)
        accumulated = cum_dep_m[e] if e >= 0 else 0.0
        closing_nbv = cum_add_m[e] - cum_dep_m[e] if e >= 0 else 0.0
        roll.opening_cost.append(round(opening_cost, 2))
        roll.additions.append(round(additions, 2))
        roll.depreciation_charge.append(round(charge, 2))
        roll.accumulated_depreciation.append(round(accumulated, 2))
        roll.closing_net_book_value.append(round(closing_nbv, 2))
        totals_by_period.append(round(charge, 2))

    if not project.fixed_assets:
        warnings.append("No fixed assets entered. Depreciation and amortisation is zero.")

    return DepreciationSchedule(
        project_id=project.id, view=view, currency=currency, periods=periods,
        assets=asset_rows, rollforward=roll, totals_by_period=totals_by_period,
        grand_total_depreciation=round(sum(totals_by_period), 2),
        total_closing_nbv=round(roll.closing_net_book_value[-1] if roll.closing_net_book_value else 0.0, 2),
        warnings=warnings,
    )


def build_summary(project: BusinessPlanProject) -> FixedAssetSummary:
    start, _years, n = pps.build_projection_periods(project)
    active = [a for a in project.fixed_assets if getattr(a, "active", True)]
    total_cost = sum(a.purchase_amount for a in active)
    annual_dep = sum(a.annual_straight_line_depreciation for a in active)
    schedule = generate_depreciation_schedule(project, "annual")
    nbv = schedule.total_closing_nbv if schedule.assets else total_cost
    currency = project.setup.currency if project.setup else "USD"
    return FixedAssetSummary(
        project_id=project.id, currency=currency,
        total_asset_cost=round(total_cost, 2), annual_depreciation=round(annual_dep, 2),
        net_book_value=round(nbv, 2), active_assets=len(active),
        loan_financed_assets=sum(1 for a in active if a.financing_source.value == "loan"),
        software_intangible_assets=sum(1 for a in active if a.category.value == "software_development"),
        total_assets=len(project.fixed_assets),
    )
