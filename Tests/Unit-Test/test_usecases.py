import pytest
from unittest.mock import AsyncMock
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase
)
from Features.Auth.Presentation.tdo import CreateUserTDO, LoginTDO, InfoUserTDO

@pytest.mark.asyncio
async def test_create_user_usecase():
    mock_repo = AsyncMock()
    expected_response = InfoUserTDO(
        user_id="mock_id_1",
        email="mock@example.com",
        name="Mock User",
        role="USER",
        status="ACTIVE"
    )
    mock_repo.create_user.return_value = expected_response

    usecase = CreateUserUseCase(mock_repo)
    tdo = CreateUserTDO(name="Mock User", email="mock@example.com", password="password123")
    result = await usecase.execute(tdo)

    assert result == expected_response
    mock_repo.create_user.assert_called_once_with(tdo)

@pytest.mark.asyncio
async def test_login_user_usecase():
    mock_repo = AsyncMock()
    expected_response = InfoUserTDO(
        user_id="mock_id_1",
        email="mock@example.com",
        name="Mock User"
    )
    mock_repo.login_user.return_value = expected_response

    usecase = LoginUserUseCase(mock_repo)
    tdo = LoginTDO(email="mock@example.com", password="password123")
    result = await usecase.execute(tdo)

    assert result == expected_response
    mock_repo.login_user.assert_called_once_with(tdo)

@pytest.mark.asyncio
async def test_get_user_by_id_usecase():
    mock_repo = AsyncMock()
    expected_response = InfoUserTDO(user_id="mock_id_1", email="mock@example.com", name="Mock User")
    mock_repo.get_user_by_id.return_value = expected_response

    usecase = GetUserByIdUseCase(mock_repo)
    result = await usecase.execute("mock_id_1")

    assert result == expected_response
    mock_repo.get_user_by_id.assert_called_once_with("mock_id_1")

@pytest.mark.asyncio
async def test_get_user_by_email_usecase():
    mock_repo = AsyncMock()
    expected_response = InfoUserTDO(user_id="mock_id_1", email="mock@example.com", name="Mock User")
    mock_repo.get_user_by_email.return_value = expected_response

    usecase = GetUserByEmailUseCase(mock_repo)
    result = await usecase.execute("mock@example.com")

    assert result == expected_response
    mock_repo.get_user_by_email.assert_called_once_with("mock@example.com")
