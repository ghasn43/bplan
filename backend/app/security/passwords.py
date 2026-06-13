"""Password hashing (bcrypt) and password-policy validation."""
from __future__ import annotations

import re

import bcrypt

# bcrypt operates on at most 72 bytes.
_MAX = 72


def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:_MAX]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8")[:_MAX], password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def validate_password_policy(password: str) -> list[str]:
    """Return a list of policy violations (empty = OK)."""
    errors = []
    if len(password) < 10:
        errors.append("at least 10 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("an uppercase letter")
    if not re.search(r"[a-z]", password):
        errors.append("a lowercase letter")
    if not re.search(r"[0-9]", password):
        errors.append("a number")
    if not re.search(r"[^A-Za-z0-9]", password):
        errors.append("a special character")
    return errors
