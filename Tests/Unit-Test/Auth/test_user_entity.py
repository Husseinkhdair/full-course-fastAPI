import pytest
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status


def test_user_entity_initialization_defaults():
    user = UserEntity(name="Hussein", email="hussein@example.com", password="hashed_password")
    assert user.name == "Hussein"
    assert user.email == "hussein@example.com"
    assert user.password == "hashed_password"
    assert user.role == Role.USER
    assert user.status == Status.ACTIVE
    assert user.id is None
    assert user.created_at is None
    assert user.updated_at is None


def test_user_entity_initialization_custom():
    user = UserEntity(
        id=123,
        name="Admin User",
        email="admin@example.com",
        password="secret_password",
        role="admin",
        status="inactive",
        created_at="2026-01-01 00:00:00",
        updated_at="2026-01-02 00:00:00"
    )
    assert user.id == "123"
    assert user.role == Role.ADMIN
    assert user.status == Status.INACTIVE
    assert user.created_at == "2026-01-01 00:00:00"
    assert user.updated_at == "2026-01-02 00:00:00"


def test_user_entity_to_dict():
    user = UserEntity(
        id="user-1",
        name="John Doe",
        email="john@example.com",
        password="password123",
        role=Role.ADMIN,
        status=Status.ACTIVE,
        created_at="2026-01-01 12:00:00",
        updated_at="2026-01-01 12:00:00"
    )
    dict_data = user.to_dict()
    assert dict_data["id"] == "user-1"
    assert dict_data["name"] == "John Doe"
    assert dict_data["email"] == "john@example.com"
    assert dict_data["password"] == "password123"
    assert dict_data["role"] == "admin"
    assert dict_data["status"] == "active"
    assert dict_data["created_at"] == "2026-01-01 12:00:00"


def test_user_entity_from_dict():
    data = {
        "_id": "507f1f77bcf86cd799439011",
        "name": "Jane Doe",
        "email": "jane@example.com",
        "password": "hashed_pass",
        "role": "user",
        "status": "active",
        "created_at": "2026-02-01 00:00:00",
        "updated_at": "2026-02-01 00:00:00"
    }
    user = UserEntity.from_dict(data)
    assert user.id == "507f1f77bcf86cd799439011"
    assert user.name == "Jane Doe"
    assert user.email == "jane@example.com"
    assert user.role == Role.USER
    assert user.status == Status.ACTIVE


def test_user_entity_string_representation():
    user = UserEntity(
        id="101",
        name="Alice",
        email="alice@example.com",
        password="pwd",
        role=Role.USER,
        status=Status.ACTIVE
    )
    user_str = str(user)
    assert "Alice" in user_str
    assert "alice@example.com" in user_str
    assert "User(" in user_str
