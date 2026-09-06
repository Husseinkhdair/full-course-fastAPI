import pytest
from Core.di import (
    get_auth_repository,
    get_create_user_usecase,
    get_login_user_usecase,
)
from Core.errors.AuthErrors import InvalidEmailOrPassword
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.LoginUserUseCase import LoginUserUseCase


@pytest.fixture
def auth_repository() -> AuthRepository:
    return get_auth_repository()


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return get_create_user_usecase(repo=auth_repository)


@pytest.fixture
def login_user_usecase(auth_repository: AuthRepository) -> LoginUserUseCase:
    return get_login_user_usecase(repo=auth_repository)


@pytest.mark.asyncio
async def test_login_user_use_case_success(
    create_user_usecase: CreateUserUseCase,
    login_user_usecase: LoginUserUseCase,
    auth_repository: AuthRepository,
):
    created_user = await create_user_usecase.execute(
        email="test_uc_login@test.com", name="test", password="password123"
    )
    assert created_user is not None

    logged_user = await login_user_usecase.execute(
        email="test_uc_login@test.com", password="password123"
    )
    assert logged_user is not None
    assert logged_user.email == "test_uc_login@test.com"
    assert logged_user.token is not None

    deleted = await auth_repository.delete_user(user_id=created_user.id)
    assert deleted is True


@pytest.mark.asyncio
async def test_login_user_use_case_invalid_password(
    create_user_usecase: CreateUserUseCase,
    login_user_usecase: LoginUserUseCase,
    auth_repository: AuthRepository,
):
    created_user = await create_user_usecase.execute(
        email="test_uc_login_wrong_pwd@test.com", name="test", password="password123"
    )
    assert created_user is not None

    with pytest.raises(InvalidEmailOrPassword):
        await login_user_usecase.execute(
            email="test_uc_login_wrong_pwd@test.com", password="wrongpassword"
        )

    deleted = await auth_repository.delete_user(user_id=created_user.id)
    assert deleted is True


@pytest.mark.asyncio
async def test_login_user_use_case_user_not_found(
    login_user_usecase: LoginUserUseCase,
):
    with pytest.raises(InvalidEmailOrPassword):
        await login_user_usecase.execute(
            email="nonexistent_login@test.com", password="password123"
        )
