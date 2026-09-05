import pytest
from unittest.mock import AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from Features.Auth.Presentation.route import router
from Features.Auth.Presentation.tdo import InfoUserTDO
from Core.di import (
    get_create_user_usecase,
    get_login_user_usecase,
    get_user_by_id_usecase,
    get_user_by_email_usecase,
    get_delete_user_usecase
)

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_register_user_route():
    mock_usecase = AsyncMock()
    mock_usecase.execute.return_value = InfoUserTDO(
        user_id="usr-1",
        name="Hussein",
        email="hussein@example.com",
        role="user",
        status="active"
    )

    app.dependency_overrides[get_create_user_usecase] = lambda: mock_usecase

    response = client.post(
        "/auth/register",
        json={"name": "Hussein", "email": "hussein@example.com", "password": "password123"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "usr-1"
    assert data["email"] == "hussein@example.com"

    app.dependency_overrides.clear()


def test_login_user_route():
    mock_usecase = AsyncMock()
    mock_usecase.execute.return_value = InfoUserTDO(
        user_id="usr-1",
        name="Hussein",
        email="hussein@example.com",
        role="user",
        status="active"
    )

    app.dependency_overrides[get_login_user_usecase] = lambda: mock_usecase

    response = client.post(
        "/auth/login",
        json={"email": "hussein@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "usr-1"

    app.dependency_overrides.clear()


def test_get_user_by_id_route():
    mock_usecase = AsyncMock()
    mock_usecase.execute.return_value = InfoUserTDO(
        user_id="usr-100",
        name="Test User",
        email="test@example.com",
        role="user",
        status="active"
    )

    app.dependency_overrides[get_user_by_id_usecase] = lambda: mock_usecase

    response = client.get("/auth/user/id/usr-100")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "usr-100"

    app.dependency_overrides.clear()


def test_get_user_by_email_route():
    mock_usecase = AsyncMock()
    mock_usecase.execute.return_value = InfoUserTDO(
        user_id="usr-100",
        name="Test User",
        email="test@example.com",
        role="user",
        status="active"
    )

    app.dependency_overrides[get_user_by_email_usecase] = lambda: mock_usecase

    response = client.get("/auth/user/email/test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

    app.dependency_overrides.clear()


def test_delete_user_route():
    mock_usecase = AsyncMock()
    mock_usecase.execute.return_value = True

    app.dependency_overrides[get_delete_user_usecase] = lambda: mock_usecase

    response = client.delete("/auth/user/id/usr-100")
    assert response.status_code == 200
    assert response.json() is True

    app.dependency_overrides.clear()
