from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_and_login():
    response = client.post("/register", json={"email": "test@example.com", "password": "secret123"})
    assert response.status_code == 201

    login_response = client.post("/token", data={"username": "test@example.com", "password": "secret123"})
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

def test_wrong_password_rejected():
    client.post("/register", json={"email": "test2@example.com", "password": "correctpassword"})
    response = client.post("/token", data={"username": "test2@example.com", "password": "wrongpassword"})
    assert response.status_code == 401

def test_protected_endpoint_requires_token():
    response = client.get("/me")
    assert response.status_code == 401   # no Authorization header sent at all

def test_protected_endpoint_works_with_valid_token():
    client.post("/register", json={"email": "test3@example.com", "password": "secret123"})
    login = client.post("/token", data={"username": "test3@example.com", "password": "secret123"})
    token = login.json()["access_token"]

    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "test3@example.com"

def test_account_locks_after_repeated_failures():
    client.post("/register", json={"email": "brute@example.com", "password": "correctpass"})

    for _ in range(5):
        response = client.post("/token", data={"username": "brute@example.com", "password": "wrong"})
        assert response.status_code == 401

    # 6th attempt locked
    response = client.post("/token", data={"username": "brute@example.com", "password": "correctpass"})
    assert response.status_code == 429