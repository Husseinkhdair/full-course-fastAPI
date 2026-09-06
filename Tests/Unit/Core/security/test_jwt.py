from datetime import timedelta
import pytest
from Core.security.Jwt import JWTPayload, generate_token, verify_token


def test_jwt_payload_dict_conversion():
    payload = JWTPayload(
        id="user_123",
        email="test@example.com",
        role="admin",
        exp=1700000000,
    )

    data = payload.to_dict()
    assert data["id"] == "user_123"
    assert data["email"] == "test@example.com"
    assert data["role"] == "admin"
    assert data["exp"] == 1700000000

    reconstructed = JWTPayload.from_dict(data)
    assert reconstructed.id == "user_123"
    assert reconstructed.email == "test@example.com"
    assert reconstructed.role == "admin"
    assert reconstructed.exp == 1700000000


def test_jwt_payload_to_dict():
    payload = JWTPayload(
        id="user_123",
        email="test@example.com",
        role="admin",
        exp=1700000000,
    )

    data = payload.to_dict()
    assert data["id"] == "user_123"
    assert data["email"] == "test@example.com"
    assert data["role"] == "admin"
    assert data["exp"] == 1700000000


def test_jwt_payload_from_dict():
    data = {
        "id": "user_123",
        "email": "test@example.com",
        "role": "admin",
        "exp": 1700000000,
    }

    payload = JWTPayload.from_dict(data)
    assert payload is not None
    assert payload.id == "user_123"
    assert payload.email == "test@example.com"
    assert payload.role == "admin"
    assert payload.exp == 1700000000


def test_jwt_payload_repr():
    payload = JWTPayload(id="user_123", email="test@example.com", role="admin")
    repr_str = repr(payload)
    assert "id=user_123" in repr_str
    assert "email=test@example.com" in repr_str
    assert "role=admin" in repr_str


def test_generate_and_verify_token():
    payload = JWTPayload(id="user_456", email="user@example.com", role="user")
    token = generate_token(payload)

    assert isinstance(token, str)
    assert len(token) > 0

    verified_payload = verify_token(token)
    assert verified_payload is not None
    assert verified_payload.id == "user_456"
    assert verified_payload.email == "user@example.com"
    assert verified_payload.role == "user"


def test_verify_invalid_token():
    invalid_token = "invalid.token.str"
    verified = verify_token(invalid_token)
    assert verified is None


def test_verify_expired_token():
    payload = JWTPayload(id="user_789")
    token = generate_token(payload, expires_delta=timedelta(seconds=-10))

    verified = verify_token(token)
    assert verified is None
