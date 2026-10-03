from app.core.security import hash_password
from app.models import User


def test_register_login_me_flow(client):
    r = client.post(
        "/api/auth/register", json={"email": "new@example.com", "password": "password123"}
    )
    assert r.status_code == 201
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"] and body["refresh_token"]

    # duplicate registration is rejected
    r2 = client.post(
        "/api/auth/register", json={"email": "new@example.com", "password": "password123"}
    )
    assert r2.status_code == 409

    # login works
    r3 = client.post(
        "/api/auth/login", json={"email": "new@example.com", "password": "password123"}
    )
    assert r3.status_code == 200

    # wrong password rejected
    r4 = client.post(
        "/api/auth/login", json={"email": "new@example.com", "password": "wrongpass99"}
    )
    assert r4.status_code == 401

    # /me with the access token
    token = body["access_token"]
    r5 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r5.status_code == 200
    assert r5.json()["email"] == "new@example.com"


def test_refresh_flow(client):
    r = client.post(
        "/api/auth/register", json={"email": "ref@example.com", "password": "password123"}
    )
    refresh = r.json()["refresh_token"]
    r2 = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert r2.status_code == 200
    assert r2.json()["access_token"]

    # an access token cannot be used as a refresh token
    access = r.json()["access_token"]
    r3 = client.post("/api/auth/refresh", json={"refresh_token": access})
    assert r3.status_code == 401


def test_me_requires_auth(client):
    r = client.get("/api/auth/me")
    assert r.status_code == 401


def test_passwords_hashed_in_db(client):
    client.post(
        "/api/auth/register", json={"email": "hash@example.com", "password": "password123"}
    )
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "hash@example.com").first()
        assert user is not None
        assert user.password_hash != "password123"
        assert verify_ok(user.password_hash, "password123")
    finally:
        db.close()


def verify_ok(password_hash: str, password: str) -> bool:
    from app.core.security import verify_password

    return verify_password(password_hash, password)
