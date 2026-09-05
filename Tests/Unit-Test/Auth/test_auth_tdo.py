import pytest
from pydantic import ValidationError
from Features.Auth.Presentation.tdo import CreateUserTDO, LoginTDO, InfoUserTDO


def test_create_user_tdo_valid():
    tdo = CreateUserTDO(name="Hussein", email="hussein@example.com", password="password123")
    assert tdo.name == "Hussein"
    assert tdo.email == "hussein@example.com"
    assert tdo.password == "password123"


def test_create_user_tdo_invalid_email():
    with pytest.raises(ValidationError):
        CreateUserTDO(name="Hussein", email="invalid-email", password="password123")


def test_create_user_tdo_short_password():
    with pytest.raises(ValidationError):
        CreateUserTDO(name="Hussein", email="hussein@example.com", password="123")


def test_login_tdo_valid():
    tdo = LoginTDO(email="user@example.com", password="securepassword")
    assert tdo.email == "user@example.com"
    assert tdo.password == "securepassword"


def test_login_tdo_invalid_email():
    with pytest.raises(ValidationError):
        LoginTDO(email="not-an-email", password="securepassword")


def test_info_user_tdo_valid():
    info = InfoUserTDO(
        user_id="user-999",
        name="User NinetyNine",
        email="user99@example.com",
        role="user",
        status="active"
    )
    assert info.user_id == "user-999"
    assert info.name == "User NinetyNine"
    assert info.email == "user99@example.com"
    assert info.role == "user"
    assert info.status == "active"
