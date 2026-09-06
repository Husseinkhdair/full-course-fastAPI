import pytest
from Core.DataBase.PostgresDB import engine
from Core.errors.AuthErrors import (
    InvalidEmailOrPassword,
    UserAlredyExists,
    UserDoesNotExists,
)
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import (
    AuthRepositoryPostgresSQl,
)
from Features.Auth.Data.Models.AuthModelPostgres import Base
from Features.Auth.Domain.Entities.UserEntity import UserEntity


@pytest.fixture
def auth_repository():
    Base.metadata.create_all(bind=engine)
    return AuthRepositoryPostgresSQl()


@pytest.mark.integration
async def test_create_user_postgres(auth_repository: AuthRepositoryPostgresSQl):
    user = await auth_repository.create_user("pg_test@test.com", "pg_test", "password123")
    assert user is not None
    assert isinstance(user, UserEntity)
    assert user.email == "pg_test@test.com"

    deleted = await auth_repository.delete_user(user.id)
    assert deleted is True


@pytest.mark.integration
async def test_delete_user_postgres(auth_repository: AuthRepositoryPostgresSQl):
    user = await auth_repository.create_user("pg_delete@test.com", "pg_test", "password123")
    assert user is not None

    deleted = await auth_repository.delete_user(user.id)
    assert deleted is True

    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.integration
async def test_get_user_by_id_postgres(auth_repository: AuthRepositoryPostgresSQl):
    user = await auth_repository.create_user("pg_id@test.com", "pg_test", "password123")
    assert user is not None

    fetched_user = await auth_repository.get_user_by_id(user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id

    await auth_repository.delete_user(user.id)

    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.integration
async def test_get_user_by_email_postgres(auth_repository: AuthRepositoryPostgresSQl):
    user = await auth_repository.create_user("pg_email@test.com", "pg_test", "password123")
    assert user is not None

    fetched_user = await auth_repository.get_user_by_email("pg_email@test.com")
    assert fetched_user is not None
    assert fetched_user.email == "pg_email@test.com"

    await auth_repository.delete_user(user.id)

    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_email("pg_email@test.com")


@pytest.mark.integration
async def test_login_user_postgres(auth_repository: AuthRepositoryPostgresSQl):
    user = await auth_repository.create_user("pg_login@test.com", "pg_test", "password123")
    assert user is not None

    logged_user = await auth_repository.login_user("pg_login@test.com", "password123")
    assert logged_user is not None
    assert logged_user.email == "pg_login@test.com"

    await auth_repository.delete_user(user.id)

    with pytest.raises(InvalidEmailOrPassword):
        await auth_repository.login_user("pg_login@test.com", "password123")


@pytest.mark.integration
async def test_create_user_already_exists_postgres(auth_repository: AuthRepositoryPostgresSQl):
    user = await auth_repository.create_user("pg_dup@test.com", "pg_test", "password123")
    assert user is not None

    with pytest.raises(UserAlredyExists):
        await auth_repository.create_user("pg_dup@test.com", "pg_test", "password123")

    await auth_repository.delete_user(user.id)
