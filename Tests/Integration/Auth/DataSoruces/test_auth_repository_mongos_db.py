from Core.errors.AuthErrors import (
    AuthError,
    InvalidEmailOrPassword,
    UserAlredyExists,
    UserDoesNotExists,
)
import pytest

from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB


@pytest.fixture
async def auth_repository():
    return AuthRepositoryMongoDB()

@pytest.mark.integration
async def test_create_user(auth_repository: AuthRepositoryMongoDB):

    user = await auth_repository.create_user(
        "test@test.com",
        "test",
        "test"
    )

    assert user is not None

    bool = await auth_repository.delete_user(user.id)

    assert bool is True

@pytest.mark.integration
async def test_delete_user(auth_repository: AuthRepositoryMongoDB):

    user = await auth_repository.create_user(
        "test@test.com",
        "test",
        "test"
    )

    assert user is not None

    bool = await auth_repository.delete_user(user.id)

    assert bool is True

    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.integration
async def test_get_user_by_id(auth_repository: AuthRepositoryMongoDB):

    user = await auth_repository.create_user(
        "test@test.com",
        "test",
        "test"
    )

    assert user is not None

    user = await auth_repository.get_user_by_id(user.id)

    assert user is not None

    bool = await auth_repository.delete_user(user.id)

    assert bool is True

    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.integration
async def test_get_user_by_email(auth_repository: AuthRepositoryMongoDB):

    user = await auth_repository.create_user(
        "test@test.com",
        "test",
        "test"
    )

    assert user is not None

    user = await auth_repository.get_user_by_email(user.email)

    assert user is not None

    bool = await auth_repository.delete_user(user.id)

    assert bool is True

    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_email(user.email)


@pytest.mark.integration
async def test_login_user(auth_repository: AuthRepositoryMongoDB):

    user = await auth_repository.create_user(
        "test@test.com",
        "test",
        "test"
    )

    assert user is not None

    user = await auth_repository.login_user(
        "test@test.com",
        "test"
    )

    assert user is not None

    bool = await auth_repository.delete_user(user.id)

    assert bool is True

    with pytest.raises(InvalidEmailOrPassword):
        await auth_repository.login_user("test@test.com", "test")



@pytest.mark.integration
async def test_create_user_already_exists(auth_repository: AuthRepositoryMongoDB):

    user = await auth_repository.create_user(
        "test@test.com",
        "test",
        "test"
    )

    assert user is not None

    with pytest.raises(UserAlredyExists):
        await auth_repository.create_user("test@test.com", "test", "test")

    bool = await auth_repository.delete_user(user.id)

    assert bool is True
