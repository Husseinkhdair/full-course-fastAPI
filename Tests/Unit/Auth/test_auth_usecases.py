import pytest
from unittest.mock import AsyncMock

from Core.errors.AuthErrors import InvalidEmailOrPassword, UserAlredyExists, UserDoesNotExists
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.DeleteUserUseCase import DeleteUserUseCase
from Features.Auth.Domain.UseCases.GetUserByEmailUseCase import GetUserByEmailUseCase
from Features.Auth.Domain.UseCases.GetUserByIdUseCase import GetUserByIdUseCase
from Features.Auth.Domain.UseCases.LoginUserUseCase import LoginUserUseCase


@pytest.fixture
def mock_repo():
    return AsyncMock(spec=AuthRepository)


@pytest.mark.asyncio
async def test_create_user_usecase_success(mock_repo):
    mock_repo.get_user_by_email.side_effect = UserDoesNotExists()
    mock_user = UserEntity(
        id="user_123",
        name="Test",
        email="test@example.com",
        password="hashed_pwd",
        role=Role.USER,
        status=Status.ACTIVE,
    )
    mock_repo.create_user.return_value = mock_user

    usecase = CreateUserUseCase(mock_repo)
    result = await usecase.execute("test@example.com", "Test", "password123")

    assert result is not None
    assert result.email == "test@example.com"
    assert result.token is not None
    mock_repo.create_user.assert_called_once_with("test@example.com", "Test", "password123")


@pytest.mark.asyncio
async def test_create_user_usecase_already_exists(mock_repo):
    existing_user = UserEntity(
        id="user_123",
        name="Existing",
        email="test@example.com",
        password="hashed_pwd",
    )
    mock_repo.get_user_by_email.return_value = existing_user

    usecase = CreateUserUseCase(mock_repo)
    with pytest.raises(UserAlredyExists):
        await usecase.execute("test@example.com", "Existing", "password123")


@pytest.mark.asyncio
async def test_login_user_usecase_success(mock_repo):
    mock_user = UserEntity(
        id="user_123",
        name="Test",
        email="test@example.com",
        password="hashed_pwd",
        role=Role.USER,
    )
    mock_repo.login_user.return_value = mock_user

    usecase = LoginUserUseCase(mock_repo)
    result = await usecase.execute("test@example.com", "password123")

    assert result is not None
    assert result.token is not None
    mock_repo.login_user.assert_called_once_with("test@example.com", "password123")


@pytest.mark.asyncio
async def test_login_user_usecase_invalid_credentials(mock_repo):
    mock_repo.login_user.side_effect = InvalidEmailOrPassword()

    usecase = LoginUserUseCase(mock_repo)
    with pytest.raises(InvalidEmailOrPassword):
        await usecase.execute("test@example.com", "wrongpassword")


@pytest.mark.asyncio
async def test_get_user_by_id_usecase(mock_repo):
    mock_user = UserEntity(id="user_123", name="Test", email="test@example.com", password="pwd")
    mock_repo.get_user_by_id.return_value = mock_user

    usecase = GetUserByIdUseCase(mock_repo)
    result = await usecase.execute("user_123")

    assert result.id == "user_123"
    mock_repo.get_user_by_id.assert_called_once_with("user_123")


@pytest.mark.asyncio
async def test_get_user_by_email_usecase(mock_repo):
    mock_user = UserEntity(id="user_123", name="Test", email="test@example.com", password="pwd")
    mock_repo.get_user_by_email.return_value = mock_user

    usecase = GetUserByEmailUseCase(mock_repo)
    result = await usecase.execute("test@example.com")

    assert result.email == "test@example.com"
    mock_repo.get_user_by_email.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_delete_user_usecase(mock_repo):
    mock_repo.delete_user.return_value = True

    usecase = DeleteUserUseCase(mock_repo)
    result = await usecase.execute("user_123")

    assert result is True
    mock_repo.delete_user.assert_called_once_with("user_123")
