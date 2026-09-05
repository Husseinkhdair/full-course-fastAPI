import pytest
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status
from Core.security.Password import hash_password, verify_password

def test_user_entity_defaults():
    user = UserEntity(name="Test", email="test@example.com", password="pass")
    assert user.name == "Test"
    assert user.email == "test@example.com"
    assert user.role == Role.USER
    assert user.status == Status.ACTIVE
    assert user.id is None

def test_user_entity_to_dict_and_from_dict():
    user = UserEntity(
        name="Hussein",
        email="hussein@example.com",
        password="secretpassword",
        role=Role.ADMIN,
        status=Status.ACTIVE,
        id="custom_id_123"
    )
    user_dict = user.to_dict()
    assert user_dict["id"] == "custom_id_123"
    assert user_dict["name"] == "Hussein"
    assert user_dict["role"] == "admin"

    reconstructed_user = UserEntity.from_dict(user_dict)
    assert reconstructed_user.id == "custom_id_123"
    assert reconstructed_user.role == Role.ADMIN
    assert reconstructed_user.email == "hussein@example.com"

def test_password_hashing():
    raw_pass = "my_secure_password"
    hashed = hash_password(raw_pass)
    assert hashed != raw_pass
    assert verify_password(raw_pass, hashed) is True
    assert verify_password("wrong_password", hashed) is False
