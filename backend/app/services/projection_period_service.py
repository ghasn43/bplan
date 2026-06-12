"""Central projection-period engine.

Single source of truth for the projection timeline, derived from project setup
(start date, period length, frequency). Both monthly and annual period sets are
generated here and reused by every projection/income-statement service.
"""
from __future__ import annotations

import calendar
from datetime import date

from dateutil.relativedelta import relativedelta

from ..models import BusinessPlanProject
from ..schemas.projection import ProjectionPeriod


def build_projection_periods(project: BusinessPlanProject) -> tuple[date, int, int]:
    """Return (start_date, years, n_months)."""
    setup = project.setup
    if setup and setup.projection_start_date and setup.projection_period:
        return setup.projection_start_date, setup.projection_period.years, setup.projection_period.years * 12
    return date(date.today().year, 1, 1), 5, 60


def get_monthly_periods(project: BusinessPlanProject) -> list[ProjectionPeriod]:
    start, _years, n = build_projection_periods(project)
    out: list[ProjectionPeriod] = []
    for i in range(n):
        d = start + relativedelta(months=i)
        last_day = calendar.monthrange(d.year, d.month)[1]
        out.append(ProjectionPeriod(
            id=f"m{i}", period_index=i, period_label=d.strftime("%b %Y"), period_type="monthly",
            start_date=date(d.year, d.month, 1), end_date=date(d.year, d.month, last_day),
            fiscal_year=d.year, projection_year=i // 12 + 1, month_number=d.month,
            quarter_number=(d.month - 1) // 3 + 1,
        ))
    return out


def get_annual_periods(project: BusinessPlanProject) -> list[ProjectionPeriod]:
    start, years, _n = build_projection_periods(project)
    out: list[ProjectionPeriod] = []
    for y in range(years):
        first = start + relativedelta(months=y * 12)
        last = start + relativedelta(months=(y + 1) * 12 - 1)
        last_day = calendar.monthrange(last.year, last.month)[1]
        out.append(ProjectionPeriod(
            id=f"y{y}", period_index=y, period_label=f"Year {y + 1}", period_type="annual",
            start_date=date(first.year, first.month, 1), end_date=date(last.year, last.month, last_day),
            fiscal_year=first.year, projection_year=y + 1,
        ))
    return out


def periods_for(project: BusinessPlanProject, mode: str) -> list[ProjectionPeriod]:
    return get_annual_periods(project) if mode == "annual" else get_monthly_periods(project)


def aggregate_monthly_to_annual(values: list[float], years: int) -> list[float]:
    """Sum each 12-month block into an annual figure."""
    return [round(sum(values[y * 12:(y + 1) * 12]), 2) for y in range(years)]


def expand_annual_to_monthly(values: list[float], n_months: int, method: str = "even") -> list[float]:
    """Spread annual figures across months. 'even' = value/12 each month."""
    out = [0.0] * n_months
    for y, v in enumerate(values):
        for m in range(12):
            t = y * 12 + m
            if t < n_months:
                out[t] = v / 12 if method == "even" else (v if m == 0 else 0.0)
    return out
