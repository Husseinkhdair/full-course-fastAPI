import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_and_login_flow():
    unique_email = "integration_test_user@example.com"
    register_payload = {
        "name": "Integration User",
        "email": unique_email,
        "password": "password123"
    }

    # 1. Register User
    response = client.post("/auth/register", json=register_payload)
    if response.status_code == 400:  # User already exists from previous run
        pass
    else:
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == unique_email
        assert data["name"] == "Integration User"
        assert "user_id" in data

    # 2. Login User
    login_payload = {
        "email": unique_email,
        "password": "password123"
    }
    login_res = client.post("/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["email"] == unique_email

    # 3. Get User By Email
    email_res = client.get(f"/auth/user/email/{unique_email}")
    assert email_res.status_code == 200
    assert email_res.json()["name"] == "Integration User"

    # 4. Get User By ID
    user_id = login_data["user_id"]
    id_res = client.get(f"/auth/user/id/{user_id}")
    assert id_res.status_code == 200
    assert id_res.json()["email"] == unique_email

def test_invalid_login():
    login_payload = {
        "email": "non_existent_user@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
