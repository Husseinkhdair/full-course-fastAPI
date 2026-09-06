import pytest
from Core.di import get_auth_repository, get_create_user_usecase
from Core.errors.AuthErrors import UserAlredyExists
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase


@pytest.fixture
def auth_repository() -> AuthRepository:
    return get_auth_repository()


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return get_create_user_usecase(repo=auth_repository)


@pytest.mark.asyncio
async def test_create_user_use_case_success(
    create_user_usecase: CreateUserUseCase, auth_repository: AuthRepository
):
    result = await create_user_usecase.execute(
        email="test_uc_create@test.com", name="test", password="password123"
    )

    assert result is not None
    assert result.email == "test_uc_create@test.com"
    assert result.token is not None

    deleted_user = await auth_repository.delete_user(user_id=result.id)
    assert deleted_user is True


@pytest.mark.asyncio
async def test_create_user_use_case_already_exists(
    create_user_usecase: CreateUserUseCase, auth_repository: AuthRepository
):
    result = await create_user_usecase.execute(
        email="test_uc_dup@test.com", name="test", password="password123"
    )
    assert result is not None

    with pytest.raises(UserAlredyExists):
        await create_user_usecase.execute(
            email="test_uc_dup@test.com", name="test", password="password123"
        )

    deleted_user = await auth_repository.delete_user(user_id=result.id)
    assert deleted_user is True
