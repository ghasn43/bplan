"""API route modules."""
from __future__ import annotations

from .balance_sheet import router as balance_sheet_router
from .cash_flow import router as cash_flow_router
from .demo import router as demo_router
from .financial_analysis import router as financial_analysis_router
from .fixed_assets import router as fixed_assets_router
from .income_statement import router as income_statement_router
from .projections import router as projections_router
from .projects import router as projects_router
from .reports import router as reports_router
from .text_plan import router as text_plan_router
from .sections import build_section_routers

__all__ = [
    "projects_router",
    "demo_router",
    "balance_sheet_router",
    "cash_flow_router",
    "financial_analysis_router",
    "fixed_assets_router",
    "income_statement_router",
    "projections_router",
    "reports_router",
    "text_plan_router",
    "build_section_routers",
]
