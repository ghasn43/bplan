"""JSON storage for users and audit logs (atomic writes, process lock)."""
from __future__ import annotations

import json
import os
import threading
from pathlib import Path

from ..models import AuditLog, User
from .base import NotFoundError


class UserStorage:
    def __init__(self, data_dir: Path) -> None:
        self._dir = Path(data_dir) / "users"
        self._dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def _path(self, user_id: str) -> Path:
        return self._dir / f"{user_id}.json"

    def list_users(self) -> list[User]:
        with self._lock:
            out = []
            for p in self._dir.glob("*.json"):
                try:
                    out.append(User.model_validate(json.loads(p.read_text(encoding="utf-8"))))
                except Exception:
                    continue
        out.sort(key=lambda u: u.created_at)
        return out

    def get(self, user_id: str) -> User:
        with self._lock:
            p = self._path(user_id)
            if not p.exists():
                raise NotFoundError(f"User {user_id!r} not found")
            return User.model_validate(json.loads(p.read_text(encoding="utf-8")))

    def get_by_email(self, email: str) -> User | None:
        email = (email or "").strip().lower()
        for u in self.list_users():
            if u.email.strip().lower() == email:
                return u
        return None

    def save(self, user: User) -> User:
        with self._lock:
            p = self._path(user.id)
            tmp = p.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(user.model_dump(mode="json"), indent=2, default=str), encoding="utf-8")
            os.replace(tmp, p)
        return user

    def delete(self, user_id: str) -> None:
        with self._lock:
            p = self._path(user_id)
            if p.exists():
                p.unlink()


class AuditStorage:
    def __init__(self, data_dir: Path) -> None:
        self._path = Path(data_dir) / "audit_log.jsonl"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def append(self, entry: AuditLog) -> None:
        with self._lock:
            with self._path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(entry.model_dump(mode="json"), default=str) + "\n")

    def list(self, limit: int = 500) -> list[AuditLog]:
        if not self._path.exists():
            return []
        with self._lock:
            lines = self._path.read_text(encoding="utf-8").splitlines()
        out = []
        for ln in lines[-limit:]:
            try:
                out.append(AuditLog.model_validate(json.loads(ln)))
            except Exception:
                continue
        out.reverse()
        return out
