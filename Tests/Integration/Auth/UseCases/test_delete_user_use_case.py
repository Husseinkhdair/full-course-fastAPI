import uuid
from Core.security.Jwt import JWTPayload, generate_token
import pytest
from Core.di import (
    get_auth_repository,
    get_create_user_usecase,
    get_delete_user_usecase as di_get_delete_user_usecase,
    get_user_by_id_usecase as di_get_user_by_id_usecase,
)
from Core.errors.AuthErrors import UserDoesNotExists
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.DeleteUserUseCase import DeleteUserUseCase
from Features.Auth.Domain.UseCases.GetUserByIdUseCase import GetUserByIdUseCase


@pytest.fixture
def auth_repository() -> AuthRepository:
    return get_auth_repository()


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return get_create_user_usecase(repo=auth_repository)


@pytest.fixture
def delete_user_usecase(auth_repository: AuthRepository) -> DeleteUserUseCase:
    return di_get_delete_user_usecase(repo=auth_repository)


@pytest.fixture
def get_user_by_id_usecase(auth_repository: AuthRepository) -> GetUserByIdUseCase:
    return di_get_user_by_id_usecase(repo=auth_repository)


@pytest.mark.asyncio
async def test_delete_user_use_case_success(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
    get_user_by_id_usecase: GetUserByIdUseCase,
):
    email = f"test_delete_{uuid.uuid4().hex[:8]}@test.com"
    created_user = await create_user_usecase.execute(
        email=email, name="test", password="password123"
    )
    assert created_user is not None

    token = generate_token(JWTPayload(id=created_user.id, email=created_user.email, role="admin"))

    deleted = await delete_user_usecase.execute(user_id=created_user.id, token=token)
    assert deleted is True

    with pytest.raises(UserDoesNotExists):
        await get_user_by_id_usecase.execute(user_id=created_user.id, role=Role.ADMIN)


@pytest.mark.asyncio
async def test_delete_user_use_case_not_found(
    delete_user_usecase: DeleteUserUseCase,
):
    token = generate_token(JWTPayload(id="admin_1", email="admin@test.com", role="admin"))
    with pytest.raises(UserDoesNotExists):
        await delete_user_usecase.execute(user_id="non_existent_delete_id_999", token=token)
