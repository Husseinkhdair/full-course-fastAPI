import logging
import pytest
from Core.Settings import SettingsApp
from Core.errors.AuthErrors import (
    UserAlredyExists,
    UserDoesNotExists,
    InvalidEmailOrPassword,
    UserNotHaveRole
)
from Core.errors.GlobleErrors import ServerError
from Core.security.Password import PasswordSecurity, hash_password, verify_password
from Core.logging_config import LoggerFilter, request_id_var, user_id_var

from Core.di import (
    get_auth_repository,
    get_create_user_usecase,
    get_login_user_usecase,
    get_user_by_id_usecase,
    get_user_by_email_usecase
)
from Core.DataBase.MongoDb import collection_users, get_mongo_client


def test_settings_defaults():
    settings = SettingsApp()
    assert settings.mongodb_url is not None
    assert settings.mongodb_name is not None
    assert settings.collection_users is not None


def test_auth_errors():
    err1 = UserAlredyExists()
    assert err1.status_code == 400
    assert err1.detail == "User alredy exists"

    err2 = UserDoesNotExists()
    assert err2.status_code == 400
    assert err2.detail == "User does not exists"

    err3 = InvalidEmailOrPassword()
    assert err3.status_code == 401
    assert err3.detail == "Invalid email or password"

    err4 = UserNotHaveRole()
    assert err4.status_code == 403
    assert err4.detail == "User not have role"

    err5 = ServerError("Internal error")
    assert err5.status_code == 500
    assert err5.detail == "Internal error"


def test_password_security():
    hashed = PasswordSecurity.hash_password("secret")
    assert PasswordSecurity.verify_password("secret", hashed) is True
    assert PasswordSecurity.verify_password("wrong", hashed) is False
    assert PasswordSecurity.verify_password("", hashed) is False
    assert PasswordSecurity.verify_password("secret", "") is False

    with pytest.raises(ValueError):
        PasswordSecurity.hash_password("")


def test_logger_filter():
    filter_obj = LoggerFilter()
    
    # Test context variable attachment to LogRecord
    request_id_token = request_id_var.set("test-request-123")
    user_id_token = user_id_var.set("user-456")
    try:
        rec = logging.LogRecord("Core.security", logging.INFO, "", 0, "test message", (), None)
        assert filter_obj.filter(rec) is True
        assert rec.request_id == "test-request-123"
        assert rec.user_id == "user-456"
    finally:
        request_id_var.reset(request_id_token)
        user_id_var.reset(user_id_token)



def test_dependency_injection_providers():
    repo = get_auth_repository()
    assert repo is not None

    create_uc = get_create_user_usecase(repo)
    assert create_uc.auth_repository == repo

    login_uc = get_login_user_usecase(repo)
    assert login_uc.auth_repository == repo

    id_uc = get_user_by_id_usecase(repo)
    assert id_uc.auth_repository == repo

    email_uc = get_user_by_email_usecase(repo)
    assert email_uc.auth_repository == repo


def test_mongodb_collection_proxy():
    client = get_mongo_client()
    assert client is not None
    assert collection_users is not None
