import pytest
from unittest.mock import AsyncMock, MagicMock
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import AuthRepositoryPostgresSQl
from Features.Auth.Presentation.tdo import CreateUserTDO, LoginTDO
from Core.errors.AuthErrors import UserAlredyExists, UserDoesNotExists, InvalidEmailOrPassword


@pytest.mark.asyncio
async def test_mongodb_repository_create_user_already_exists():
    repo = AuthRepositoryMongoDB()
    repo.user_collection = AsyncMock()
    repo.user_collection.find_one.return_value = {"email": "existing@example.com"}

    tdo = CreateUserTDO(name="Existing User", email="existing@example.com", password="password123")

    with pytest.raises(UserAlredyExists):
        await repo.create_user(tdo)


@pytest.mark.asyncio
async def test_mongodb_repository_login_invalid_credentials():
    repo = AuthRepositoryMongoDB()
    repo.user_collection = AsyncMock()
    repo.user_collection.find_one.return_value = None

    tdo = LoginTDO(email="unknown@example.com", password="wrongpassword")

    with pytest.raises(InvalidEmailOrPassword):
        await repo.login_user(tdo)


@pytest.mark.asyncio
async def test_mongodb_repository_get_by_id_not_found():
    repo = AuthRepositoryMongoDB()
    repo.user_collection = AsyncMock()
    repo.user_collection.find_one.return_value = None

    with pytest.raises(UserDoesNotExists):
        await repo.get_user_by_id("nonexistent-id")


@pytest.mark.asyncio
async def test_postgres_repository_create_user_already_exists():
    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = MagicMock()

    repo = AuthRepositoryPostgresSQl(db=mock_db)
    tdo = CreateUserTDO(name="Existing User", email="existing@example.com", password="password123")

    with pytest.raises(UserAlredyExists):
        await repo.create_user(tdo)


@pytest.mark.asyncio
async def test_postgres_repository_login_not_found():
    mock_db = MagicMock()
    mock_db.execute.return_value.scalars.return_value.first.return_value = None

    repo = AuthRepositoryPostgresSQl(db=mock_db)
    tdo = LoginTDO(email="unknown@example.com", password="password123")

    with pytest.raises(InvalidEmailOrPassword):
        await repo.login_user(tdo)
