import pytest
from Core.di import (
    get_auth_repository,
    get_create_user_usecase,
    get_user_by_id_usecase as di_get_user_by_id_usecase,
)
from Core.errors.AuthErrors import UserDoesNotExists
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.GetUserByIdUseCase import GetUserByIdUseCase


@pytest.fixture
def auth_repository() -> AuthRepository:
    return get_auth_repository()


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return get_create_user_usecase(repo=auth_repository)


@pytest.fixture
def get_user_by_id_usecase(auth_repository: AuthRepository) -> GetUserByIdUseCase:
    return di_get_user_by_id_usecase(repo=auth_repository)


@pytest.mark.asyncio
async def test_get_user_by_id_use_case_success(
    create_user_usecase: CreateUserUseCase,
    get_user_by_id_usecase: GetUserByIdUseCase,
    auth_repository: AuthRepository,
):
    created_user = await create_user_usecase.execute(
        email="test_uc_get_id@test.com", name="test", password="password123"
    )
    assert created_user is not None

    fetched_user = await get_user_by_id_usecase.execute(user_id=created_user.id)
    assert fetched_user is not None
    assert fetched_user.id == created_user.id
    assert fetched_user.email == "test_uc_get_id@test.com"

    deleted = await auth_repository.delete_user(user_id=created_user.id)
    assert deleted is True


@pytest.mark.asyncio
async def test_get_user_by_id_use_case_not_found(
    get_user_by_id_usecase: GetUserByIdUseCase,
):
    with pytest.raises(UserDoesNotExists):
        await get_user_by_id_usecase.execute(user_id="non_existent_id_999")
