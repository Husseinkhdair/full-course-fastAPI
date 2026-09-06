import pytest
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from Core.di import (
    get_create_user_usecase,
    get_delete_user_usecase,
    get_login_user_usecase,
    get_user_by_email_usecase,
    get_user_by_id_usecase,
)
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status
from main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_register_user_route(client):
    mock_usecase = AsyncMock()
    mock_user = UserEntity(
        id="user_123",
        name="Hussein",
        email="hussein@gmail.com",
        password="hashed_pwd",
        role=Role.USER,
        status=Status.ACTIVE,
    )
    mock_user.token = "sample_jwt_token"
    mock_usecase.execute.return_value = mock_user

    app.dependency_overrides[get_create_user_usecase] = lambda: mock_usecase

    response = client.post(
        "/auth/register",
        json={"name": "Hussein", "email": "hussein@gmail.com", "password": "password123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "hussein@gmail.com"
    assert data["name"] == "Hussein"
    assert data["token"] == "sample_jwt_token"

    app.dependency_overrides.clear()


def test_login_user_route(client):
    mock_usecase = AsyncMock()
    mock_user = UserEntity(
        id="user_123",
        name="Hussein",
        email="hussein@gmail.com",
        password="hashed_pwd",
        role=Role.USER,
        status=Status.ACTIVE,
    )
    mock_user.token = "sample_jwt_token"
    mock_usecase.execute.return_value = mock_user

    app.dependency_overrides[get_login_user_usecase] = lambda: mock_usecase

    response = client.post(
        "/auth/login",
        json={"email": "hussein@gmail.com", "password": "password123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "hussein@gmail.com"
    assert data["token"] == "sample_jwt_token"

    app.dependency_overrides.clear()


def test_get_user_by_id_route(client):
    mock_usecase = AsyncMock()
    mock_user = UserEntity(
        id="user_123",
        name="Hussein",
        email="hussein@gmail.com",
        password="hashed_pwd",
    )
    mock_usecase.execute.return_value = mock_user

    app.dependency_overrides[get_user_by_id_usecase] = lambda: mock_usecase

    response = client.get("/auth/user/id/user_123")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user_123"

    app.dependency_overrides.clear()


def test_get_user_by_email_route(client):
    mock_usecase = AsyncMock()
    mock_user = UserEntity(
        id="user_123",
        name="Hussein",
        email="hussein@gmail.com",
        password="hashed_pwd",
    )
    mock_usecase.execute.return_value = mock_user

    app.dependency_overrides[get_user_by_email_usecase] = lambda: mock_usecase

    response = client.get("/auth/user/email/hussein@gmail.com")

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "hussein@gmail.com"

    app.dependency_overrides.clear()


def test_delete_user_route(client):
    mock_usecase = AsyncMock()
    mock_usecase.execute.return_value = True

    app.dependency_overrides[get_delete_user_usecase] = lambda: mock_usecase

    response = client.delete("/auth/user/id/user_123")

    assert response.status_code == 200
    assert response.json() is True

    app.dependency_overrides.clear()
