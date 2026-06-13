"""Auth dependencies. The middleware authenticates the request and attaches the
resolved ``User`` to ``request.state.user``; these helpers expose it to routes."""
from __future__ import annotations

from fastapi import HTTPException, Request, status

from ..models import User


def get_current_user(request: Request) -> User:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def get_current_active_user(request: Request) -> User:
    user = get_current_user(request)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
    return user


def require_admin(request: Request) -> User:
    user = get_current_active_user(request)
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return user


def authorized_company_ids(user: User) -> list[str] | None:
    """None = all companies (admin); otherwise the single assigned company."""
    if user.role == "admin":
        return None
    return [user.company_id] if user.company_id else []
