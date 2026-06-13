"""Demo-company loading service.

The committed JSON seed (``app/seeds/demo_aquapure_smart_filters.json``) is the
runtime source of truth. It is regenerated from :mod:`demo_builder` whenever the
schema changes (see ``scripts/generate_demo.py``).
"""
from __future__ import annotations

import json
from pathlib import Path

from ..models import BusinessPlanProject
from ..storage.base import StorageBackend
from .completion import build_completion_report
from .demo_builder import DEMO_PROJECT_ID

DEMO_JSON_PATH = Path(__file__).resolve().parent.parent / "seeds" / "demo_aquapure_smart_filters.json"

DEMO_SUBTITLE = "Complete 5-year UAE smart water filtration business plan scenario"
DEMO_TAGS = [
    "Product Sales",
    "Installation",
    "Maintenance",
    "Subscription",
    "UAE VAT",
    "Working Capital",
]


def _load_demo_document() -> BusinessPlanProject:
    """Read + validate the demo project from its JSON seed file."""
    if DEMO_JSON_PATH.exists():
        data = json.loads(DEMO_JSON_PATH.read_text(encoding="utf-8"))
        return BusinessPlanProject.model_validate(data)
    # Fallback: build from code if the JSON artifact is missing.
    from .demo_builder import build_demo_project

    return build_demo_project()


def load_aquapure(storage: StorageBackend) -> BusinessPlanProject:
    """Create or *reset* the AquaPure demo project under its stable ID."""
    project = _load_demo_document()
    project.id = DEMO_PROJECT_ID
    storage.save_project(project)
    return project


def aquapure_preview(storage: StorageBackend) -> dict:
    """Lightweight metadata for the 'Load Demo Company' card."""
    project = _load_demo_document()
    completion = build_completion_report(project)
    total_funding = (
        project.financing.equity.founder_capital
        + project.financing.equity.investor_equity
        + sum(loan.amount for loan in project.financing.loans)
        + sum(grant.amount for grant in project.financing.grants)
    )
    setup = project.setup
    return {
        "id": DEMO_PROJECT_ID,
        "name": project.name,
        # Company and project names are independent — no fallback between them.
        "company_name": setup.business_name if setup else "",
        "project_name": setup.project_name if setup else "",
        "business_name": setup.business_name if setup else "",  # legacy alias
        "subtitle": DEMO_SUBTITLE,
        "description": DEMO_SUBTITLE,
        "tags": DEMO_TAGS,
        "currency": project.setup.currency if project.setup else "AED",
        "projection_period": project.setup.projection_period.value if project.setup else None,
        "already_loaded": storage.exists(DEMO_PROJECT_ID),
        "completion_percent": completion.completion_percent,
        "metrics": {
            "products": len(project.products),
            "revenue_streams": len(project.revenue),
            "direct_cost_items": len(project.direct_costs),
            "staff_roles": len(project.staffing),
            "operating_expenses": len(project.operating_expenses),
            "startup_costs": len(project.startup_costs),
            "fixed_assets": len(project.fixed_assets),
            "loans": len(project.financing.loans),
            "scenarios": len(project.scenarios),
            "total_funding": total_funding,
        },
    }
