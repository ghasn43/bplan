"""Authentication, RBAC and tenant-isolation tests."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.models import Company, User
from app.security.passwords import hash_password
from app.storage import get_company_storage, get_storage, get_user_storage

ADMIN_EMAIL = settings.admin_email
ADMIN_PW = settings.admin_password


@pytest.fixture(scope="module")
def env():
    """Two companies, each with a project, and one user assigned to company A."""
    settings.auth_enabled = False  # set up data as admin
    companies = get_company_storage()
    storage = get_storage()
    users = get_user_storage()

    ca = Company(id="co_a_test", company_name="Alpha Co", status="active")
    cb = Company(id="co_b_test", company_name="Beta Co", status="active")
    companies.save_company(ca)
    companies.save_company(cb)

    from app.models import BusinessPlanProject
    pa = BusinessPlanProject(id="proj_a_test", name="Alpha Project", company_id="co_a_test")
    pb = BusinessPlanProject(id="proj_b_test", name="Beta Project", company_id="co_b_test")
    storage.save_project(pa)
    storage.save_project(pb)

    # ensure admin exists
    if not users.get_by_email(ADMIN_EMAIL):
        users.save(User(email=ADMIN_EMAIL, full_name="Admin", role="admin",
                        password_hash=hash_password(ADMIN_PW), is_active=True))
    # user assigned to company A
    existing = users.get_by_email("alpha_user@test.com")
    if existing:
        users.delete(existing.id)
    ua = User(email="alpha_user@test.com", full_name="Alpha User", role="user",
              company_id="co_a_test", password_hash=hash_password("UserPass123!"), is_active=True)
    users.save(ua)
    yield {"ca": ca, "cb": cb, "ua": ua}
    # cleanup
    for pid in ("proj_a_test", "proj_b_test"):
        try:
            storage.delete_project(pid)
        except Exception:
            pass
    companies.delete_company("co_a_test")
    companies.delete_company("co_b_test")
    users.delete(ua.id)


def _client():
    return TestClient(app)


def _login(client, email, password):
    return client.post("/api/auth/login", json={"email": email, "password": password})


# 1. Admin can log in
def test_admin_login(env, auth_on):
    with _client() as c:
        r = _login(c, ADMIN_EMAIL, ADMIN_PW)
        assert r.status_code == 200
        assert r.json()["user"]["role"] == "admin"
        assert "password_hash" not in r.json()["user"]  # 22: never exposed


# 2. Normal user can log in
def test_user_login(env, auth_on):
    with _client() as c:
        r = _login(c, "alpha_user@test.com", "UserPass123!")
        assert r.status_code == 200
        assert r.json()["user"]["company_id"] == "co_a_test"


# 3. Invalid password rejected (generic message)
def test_invalid_password(env, auth_on):
    with _client() as c:
        r = _login(c, "alpha_user@test.com", "wrong")
        assert r.status_code == 401
        assert r.json()["detail"] == "Invalid email or password."


# 4. Unauthenticated request is rejected
def test_requires_auth(env, auth_on):
    with _client() as c:
        assert c.get("/api/projects").status_code == 401


# 5. User sees only their company's projects
def test_user_sees_own_projects(env, auth_on):
    with _client() as c:
        _login(c, "alpha_user@test.com", "UserPass123!")
        ids = {p["id"] for p in c.get("/api/projects").json()}
        assert "proj_a_test" in ids
        assert "proj_b_test" not in ids


# 6. User cannot access another company's project (IDOR → 404)
def test_user_cannot_access_other_project(env, auth_on):
    with _client() as c:
        _login(c, "alpha_user@test.com", "UserPass123!")
        assert c.get("/api/projects/proj_a_test").status_code == 200
        assert c.get("/api/projects/proj_b_test").status_code == 404
        # nested route is also blocked
        assert c.get("/api/projects/proj_b_test/income-statement").status_code == 404


# 7. Admin can access all projects
def test_admin_access_all(env, auth_on):
    with _client() as c:
        _login(c, ADMIN_EMAIL, ADMIN_PW)
        assert c.get("/api/projects/proj_a_test").status_code == 200
        assert c.get("/api/projects/proj_b_test").status_code == 200


# 8. User cannot reach admin routes
def test_user_blocked_from_admin(env, auth_on):
    with _client() as c:
        _login(c, "alpha_user@test.com", "UserPass123!")
        assert c.get("/api/admin/users").status_code == 403


# 9. Admin can create + assign a user; reassignment changes access
def test_admin_user_management(env, auth_on):
    with _client() as c:
        _login(c, ADMIN_EMAIL, ADMIN_PW)
        r = c.post("/api/admin/users", json={
            "email": "mover@test.com", "full_name": "Mover", "role": "user",
            "company_id": "co_a_test", "temporary_password": "MoverPass123!",
        })
        assert r.status_code == 201
        uid = r.json()["id"]
        assert "password_hash" not in r.json()
        # reassign to company B
        rr = c.put(f"/api/admin/users/{uid}/company-assignment", json={"company_id": "co_b_test"})
        assert rr.status_code == 200
        assert rr.json()["company_id"] == "co_b_test"
        get_user_storage().delete(uid)


# 10. Disabled user cannot log in
def test_disabled_user(env, auth_on):
    users = get_user_storage()
    u = users.get_by_email("alpha_user@test.com")
    u.is_active = False
    users.save(u)
    try:
        with _client() as c:
            assert _login(c, "alpha_user@test.com", "UserPass123!").status_code == 401
    finally:
        u.is_active = True
        u.failed_login_attempts = 0
        u.locked_until = None
        users.save(u)


# 11. /me requires auth and returns the current user (no hash)
def test_me(env, auth_on):
    with _client() as c:
        _login(c, ADMIN_EMAIL, ADMIN_PW)
        r = c.get("/api/auth/me")
        assert r.status_code == 200
        assert "password_hash" not in r.json()


# 12. Logout clears the session
def test_logout(env, auth_on):
    with _client() as c:
        _login(c, ADMIN_EMAIL, ADMIN_PW)
        assert c.get("/api/auth/me").status_code == 200
        c.post("/api/auth/logout")
        assert c.get("/api/auth/me").status_code == 401


# 13. Five failed logins lock the account
def test_lockout(env, auth_on):
    users = get_user_storage()
    u = User(email="lockme@test.com", full_name="Lock", role="user", company_id="co_a_test",
             password_hash=hash_password("Right123!@#"), is_active=True)
    users.save(u)
    try:
        with _client() as c:
            for _ in range(settings.max_failed_logins):
                c.post("/api/auth/login", json={"email": "lockme@test.com", "password": "bad"})
            r = c.post("/api/auth/login", json={"email": "lockme@test.com", "password": "Right123!@#"})
            assert r.status_code == 423  # locked
    finally:
        users.delete(u.id)


# 14. Normal user must have a company (validation)
def test_user_requires_company(env, auth_on):
    with _client() as c:
        _login(c, ADMIN_EMAIL, ADMIN_PW)
        r = c.post("/api/admin/users", json={
            "email": "nocompany@test.com", "full_name": "X", "role": "user",
            "company_id": None, "temporary_password": "NoCompany123!",
        })
        assert r.status_code == 400
