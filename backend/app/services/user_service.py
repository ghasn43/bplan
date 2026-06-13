"""User management service (admin operations)."""
from __future__ import annotations

from ..models import User
from ..security.passwords import hash_password, validate_password_policy
from ..storage import get_company_storage, get_user_storage
from ..utils.ids import utcnow


class UserError(Exception):
    """Invalid user operation (mapped to HTTP 400/404/409)."""


def to_public(user: User):
    from ..schemas.user import UserPublic
    return UserPublic(
        id=user.id, email=user.email, username=user.username, full_name=user.full_name,
        role=user.role, company_id=user.company_id, is_active=user.is_active,
        must_change_password=user.must_change_password, last_login_at=user.last_login_at,
        created_at=user.created_at, updated_at=user.updated_at,
    )


def list_users() -> list[User]:
    return get_user_storage().list_users()


def get_user(user_id: str) -> User:
    return get_user_storage().get(user_id)


def _validate_role_company(role: str, company_id: str | None):
    if role not in ("admin", "user"):
        raise UserError("Role must be 'admin' or 'user'.")
    if role == "user" and not company_id:
        raise UserError("A normal user must be assigned to a company.")
    if company_id and not get_company_storage().exists(company_id):
        raise UserError("Assigned company does not exist.")


def create_user(data, *, created_by_id: str | None) -> User:
    store = get_user_storage()
    email = data.email.strip().lower()
    if store.get_by_email(email):
        raise UserError("A user with this email already exists.")
    _validate_role_company(data.role, data.company_id)
    problems = validate_password_policy(data.temporary_password)
    if problems:
        raise UserError("Temporary password needs " + ", ".join(problems) + ".")
    user = User(
        email=email, username=data.username, full_name=data.full_name, role=data.role,
        company_id=data.company_id if data.role == "user" else (data.company_id or None),
        password_hash=hash_password(data.temporary_password),
        must_change_password=data.must_change_password, is_active=True, is_verified=False,
        created_by_user_id=created_by_id,
    )
    return store.save(user)


def update_user(user_id: str, data) -> User:
    store = get_user_storage()
    user = store.get(user_id)
    for field in ("full_name", "username", "notes"):
        v = getattr(data, field, None)
        if v is not None:
            setattr(user, field, v)
    if getattr(data, "role", None) is not None:
        _validate_role_company(data.role, user.company_id)
        user.role = data.role
    if getattr(data, "is_active", None) is not None:
        user.is_active = data.is_active
    user.updated_at = utcnow()
    return store.save(user)


def set_active(user_id: str, active: bool) -> User:
    store = get_user_storage()
    user = store.get(user_id)
    user.is_active = active
    user.updated_at = utcnow()
    return store.save(user)


def assign_company(user_id: str, company_id: str | None) -> User:
    store = get_user_storage()
    user = store.get(user_id)
    if user.role == "user" and not company_id:
        raise UserError("A normal user must be assigned to a company.")
    if company_id and not get_company_storage().exists(company_id):
        raise UserError("Company does not exist.")
    user.company_id = company_id
    user.updated_at = utcnow()
    return store.save(user)


def reset_password(user_id: str, temporary_password: str, must_change: bool = True) -> User:
    store = get_user_storage()
    user = store.get(user_id)
    problems = validate_password_policy(temporary_password)
    if problems:
        raise UserError("Password needs " + ", ".join(problems) + ".")
    user.password_hash = hash_password(temporary_password)
    user.must_change_password = must_change
    user.failed_login_attempts = 0
    user.locked_until = None
    user.updated_at = utcnow()
    return store.save(user)


def delete_user(user_id: str) -> None:
    get_user_storage().delete(user_id)
