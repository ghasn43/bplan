"""FastAPI application entrypoint.

Run with::

    uvicorn app.main:app --reload
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import __version__
from .config import settings
from .routes import (
    balance_sheet_router,
    build_section_routers,
    cash_flow_router,
    demo_router,
    financial_analysis_router,
    fixed_assets_router,
    income_statement_router,
    projections_router,
    projects_router,
    reports_router,
    text_plan_router,
)
from .services.seed import seed_if_empty
from .storage import get_storage

logger = logging.getLogger("businessplan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.seed_on_startup:
        seed_if_empty(get_storage())
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "Backend for a professional business-plan financial projection app. "
        "Captures all assumptions required to later generate P&L, cash flow, "
        "and balance sheet projections."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Log the full traceback and return the real error to the client.

    Without this, an unhandled error surfaces in the UI as an opaque
    "Request failed (500)". Here we include the exception type + message so the
    cause (e.g. a project file from an older schema) is visible immediately.
    """
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
    )


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok", "version": __version__}


# Project-level routes + generated section routes.
app.include_router(projects_router, prefix=settings.api_prefix)
app.include_router(demo_router, prefix=settings.api_prefix)
app.include_router(income_statement_router, prefix=settings.api_prefix)
app.include_router(balance_sheet_router, prefix=settings.api_prefix)
app.include_router(cash_flow_router, prefix=settings.api_prefix)
app.include_router(financial_analysis_router, prefix=settings.api_prefix)
app.include_router(projections_router, prefix=settings.api_prefix)
# Fixed-asset schedule/summary/single routes registered before the generic
# section router so static sub-paths (e.g. /summary) resolve correctly.
app.include_router(fixed_assets_router, prefix=settings.api_prefix)
app.include_router(reports_router, prefix=settings.api_prefix)
app.include_router(text_plan_router, prefix=settings.api_prefix)
for section_router in build_section_routers():
    app.include_router(section_router, prefix=settings.api_prefix)
