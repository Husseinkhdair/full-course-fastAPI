from datetime import timedelta
import time
import pytest
from Core.security.Jwt import JWTPayload, generate_token, verify_token


def test_jwt_payload_dict_conversion():
    payload = JWTPayload(
        sub="user_123",
        email="test@example.com",
        role="admin",
        extra={"custom_field": "custom_value"},
    )

    data = payload.to_dict()
    assert data["sub"] == "user_123"
    assert data["email"] == "test@example.com"
    assert data["role"] == "admin"
    assert data["custom_field"] == "custom_value"

    reconstructed = JWTPayload.from_dict(data)
    assert reconstructed.sub == "user_123"
    assert reconstructed.email == "test@example.com"
    assert reconstructed.role == "admin"
    assert reconstructed.extra.get("custom_field") == "custom_value"


def test_generate_and_verify_token():
    payload = JWTPayload(sub="user_456", email="user@example.com", role="user")
    token = generate_token(payload)

    assert isinstance(token, str)
    assert len(token) > 0

    verified_payload = verify_token(token)
    assert verified_payload is not None
    assert verified_payload.sub == "user_456"
    assert verified_payload.email == "user@example.com"
    assert verified_payload.role == "user"


def test_verify_invalid_token():
    invalid_token = "invalid.token.str"
    verified = verify_token(invalid_token)
    assert verified is None


def test_verify_expired_token():
    payload = JWTPayload(sub="user_789")
    token = generate_token(payload, expires_delta=timedelta(seconds=-10))

    verified = verify_token(token)
    assert verified is None
