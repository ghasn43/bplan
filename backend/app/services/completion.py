"""Completion + review engine.

Computes per-section status, an overall completion percentage, and the
cross-field warnings surfaced on the Review page (Page 14).
"""
from __future__ import annotations

from ..models import (
    BusinessPlanProject,
    CompletionReport,
    ReviewStatus,
    SectionStatus,
)
from .registry import COLLECTION_SECTIONS, SECTION_ORDER, SINGLETON_SECTIONS


def _singleton_complete(spec, value) -> tuple[bool, list[str]]:
    if value is None:
        return False, list(spec.required_fields) or ["section not started"]
    missing = []
    for f in spec.required_fields:
        if getattr(value, f, None) in (None, ""):
            missing.append(f)
    # A singleton with no required_fields counts complete once it exists.
    return (len(missing) == 0), missing


def _section_status(project: BusinessPlanProject, key: str) -> SectionStatus:
    if key in SINGLETON_SECTIONS:
        spec = SINGLETON_SECTIONS[key]
        value = getattr(project, spec.attr)
        complete, missing = _singleton_complete(spec, value)
        return SectionStatus(
            key=spec.key,
            label=spec.label,
            complete=complete,
            required=spec.required,
            missing_fields=missing,
        )

    spec = COLLECTION_SECTIONS[key]
    items = getattr(project, spec.attr)
    count = len(items)
    # A collection section counts as "complete" once it holds at least one
    # item — this drives a meaningful progress bar across all 13 sections.
    return SectionStatus(
        key=spec.key,
        label=spec.label,
        complete=count > 0,
        required=spec.required,
        item_count=count,
    )


def build_completion_report(project: BusinessPlanProject) -> CompletionReport:
    sections = [_section_status(project, key) for key in SECTION_ORDER]
    completed = [s for s in sections if s.complete]

    percent = round(100 * len(completed) / len(sections)) if sections else 0
    return CompletionReport(
        project_id=project.id,
        completion_percent=percent,
        completed_sections=sum(1 for s in sections if s.complete),
        total_sections=len(sections),
        sections=sections,
    )


# --------------------------------------------------------------------------
# Cross-field validation warnings (non-blocking) + blocking issues
# --------------------------------------------------------------------------
def _estimated_unit_cost(product, items) -> float:
    """Per-unit direct cost for a product from all applicable cost items.

    Two passes: first sum per-unit amount costs (the "purchased cost" base),
    then add percentage methods. ``percent_of_purchase_cost`` is charged on the
    per-unit base; ``percent_of_revenue`` / ``percent_of_selling_price`` on the
    selling price. Monthly and one-time pooled costs are excluded (not per-unit).
    """
    from ..models.enums import CostCalculationMethod as M

    price = product.selling_price
    applicable = [i for i in items if i.active and i.applies_to(product.id)]

    per_unit_base = sum(i.amount for i in applicable if i.calculation_method.is_per_unit)

    total = per_unit_base
    for item in applicable:
        m = item.calculation_method
        if m in (M.PERCENT_OF_REVENUE, M.PERCENT_OF_SELLING_PRICE):
            total += (item.percent / 100) * price
        elif m == M.PERCENT_OF_PURCHASE_COST:
            total += (item.percent / 100) * per_unit_base
    return total


def _gross_margin_warnings(project: BusinessPlanProject) -> list[str]:
    warnings: list[str] = []
    for product in project.products:
        if product.selling_price <= 0:
            continue
        unit_cost = _estimated_unit_cost(product, project.direct_costs)
        margin = product.selling_price - unit_cost
        if margin < 0:
            warnings.append(
                f"'{product.name}' has a negative estimated gross margin "
                f"(price {product.selling_price:.2f} < direct cost {unit_cost:.2f})."
            )
    return warnings


def _unassigned_cost_warnings(project: BusinessPlanProject) -> list[str]:
    unassigned = [c for c in project.direct_costs if c.is_unassigned]
    if not unassigned:
        return []
    return [
        f"{len(unassigned)} direct cost item"
        f"{'s are' if len(unassigned) > 1 else ' is'} unassigned — associate "
        "them with a product/service or mark them as shared."
    ]


def _growth_warnings(project: BusinessPlanProject) -> list[str]:
    warnings: list[str] = []
    name_by_id = {p.id: p.name for p in project.products}
    for r in project.revenue:
        if r.annual_growth_rate is not None and abs(r.annual_growth_rate) > 100:
            warnings.append(
                f"'{name_by_id.get(r.product_id, r.product_id)}' annual growth rate "
                f"of {r.annual_growth_rate:.0f}% is extreme — double-check this."
            )
    return warnings


def _working_capital_warnings(project: BusinessPlanProject) -> list[str]:
    wc = project.working_capital
    if wc is None:
        return []
    if wc.accounts_receivable_days > 2 * max(wc.accounts_payable_days, 1):
        return [
            "Receivable days are much longer than payable days — this can cause "
            "a cash-flow squeeze."
        ]
    return []


def build_review_status(project: BusinessPlanProject) -> ReviewStatus:
    completion = build_completion_report(project)

    blocking = [
        f"Required section incomplete: {s.label}"
        for s in completion.sections
        if s.required and not s.complete
    ]

    warnings: list[str] = []
    warnings += _gross_margin_warnings(project)
    warnings += _unassigned_cost_warnings(project)
    warnings += _growth_warnings(project)
    warnings += _working_capital_warnings(project)

    return ReviewStatus(
        project_id=project.id,
        completion=completion,
        ready_for_projection=len(blocking) == 0,
        blocking_issues=blocking,
        warnings=warnings,
    )
