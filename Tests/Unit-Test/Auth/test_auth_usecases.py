import pytest
from unittest.mock import AsyncMock

from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.LoginUserUseCase import LoginUserUseCase
from Features.Auth.Domain.UseCases.GetUserByIdUseCase import GetUserByIdUseCase
from Features.Auth.Domain.UseCases.GetUserByEmailUseCase import GetUserByEmailUseCase
from Features.Auth.Domain.UseCases.DeleteUserUseCase import DeleteUserUseCase
from Features.Auth.Presentation.tdo import CreateUserTDO, LoginTDO, InfoUserTDO


@pytest.fixture
def mock_auth_repository():
    return AsyncMock()


@pytest.mark.asyncio
async def test_create_user_usecase(mock_auth_repository):
    usecase = CreateUserUseCase(mock_auth_repository)
    tdo = CreateUserTDO(name="Test User", email="test@example.com", password="password123")
    expected_result = InfoUserTDO(user_id="1", name="Test User", email="test@example.com")
    
    mock_auth_repository.create_user.return_value = expected_result
    
    result = await usecase.execute(tdo)
    assert result == expected_result
    mock_auth_repository.create_user.assert_called_once_with(tdo)


@pytest.mark.asyncio
async def test_login_user_usecase(mock_auth_repository):
    usecase = LoginUserUseCase(mock_auth_repository)
    tdo = LoginTDO(email="test@example.com", password="password123")
    expected_result = InfoUserTDO(user_id="1", name="Test User", email="test@example.com")

    mock_auth_repository.login_user.return_value = expected_result

    result = await usecase.execute(tdo)
    assert result == expected_result
    mock_auth_repository.login_user.assert_called_once_with(tdo)


@pytest.mark.asyncio
async def test_get_user_by_id_usecase(mock_auth_repository):
    usecase = GetUserByIdUseCase(mock_auth_repository)
    expected_result = InfoUserTDO(user_id="usr-123", name="Test User", email="test@example.com")

    mock_auth_repository.get_user_by_id.return_value = expected_result

    result = await usecase.execute("usr-123")
    assert result == expected_result
    mock_auth_repository.get_user_by_id.assert_called_once_with("usr-123")


@pytest.mark.asyncio
async def test_get_user_by_email_usecase(mock_auth_repository):
    usecase = GetUserByEmailUseCase(mock_auth_repository)
    expected_result = InfoUserTDO(user_id="usr-123", name="Test User", email="test@example.com")

    mock_auth_repository.get_user_by_email.return_value = expected_result

    result = await usecase.execute("test@example.com")
    assert result == expected_result
    mock_auth_repository.get_user_by_email.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_delete_user_usecase(mock_auth_repository):
    usecase = DeleteUserUseCase(mock_auth_repository)
    mock_auth_repository.delete_user.return_value = True

    result = await usecase.execute("usr-123")
    assert result is True
    mock_auth_repository.delete_user.assert_called_once_with("usr-123")
