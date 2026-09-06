import pytest
from Core.di import (
    get_auth_repository,
    get_create_user_usecase,
    get_user_by_email_usecase as di_get_user_by_email_usecase,
)
from Core.errors.AuthErrors import UserDoesNotExists
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.GetUserByEmailUseCase import GetUserByEmailUseCase


@pytest.fixture
def auth_repository() -> AuthRepository:
    return get_auth_repository()


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return get_create_user_usecase(repo=auth_repository)


@pytest.fixture
def get_user_by_email_usecase(auth_repository: AuthRepository) -> GetUserByEmailUseCase:
    return di_get_user_by_email_usecase(repo=auth_repository)


@pytest.mark.asyncio
async def test_get_user_by_email_use_case_success(
    create_user_usecase: CreateUserUseCase,
    get_user_by_email_usecase: GetUserByEmailUseCase,
    auth_repository: AuthRepository,
):
    created_user = await create_user_usecase.execute(
        email="test_uc_get_email@test.com", name="test", password="password123"
    )
    assert created_user is not None

    fetched_user = await get_user_by_email_usecase.execute(email="test_uc_get_email@test.com")
    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.email == "test_uc_get_email@test.com"

    deleted = await auth_repository.delete_user(user_id=created_user.id)
    assert deleted is True


@pytest.mark.asyncio
async def test_get_user_by_email_use_case_not_found(
    get_user_by_email_usecase: GetUserByEmailUseCase,
):
    with pytest.raises(UserDoesNotExists):
        await get_user_by_email_usecase.execute(email="non_existent_email@test.com")
