"""Shared test configuration.

Authentication is enforced in production but **disabled by default for the test
suite** so the existing endpoint tests run as a system admin. The dedicated
auth/authorization tests re-enable it explicitly via the ``auth_on`` fixture.
"""
from __future__ import annotations

import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def _auth_disabled_by_default():
    prev = settings.auth_enabled
    settings.auth_enabled = False
    yield
    settings.auth_enabled = prev


@pytest.fixture
def auth_on():
    prev = settings.auth_enabled
    settings.auth_enabled = True
    yield
    settings.auth_enabled = prev
