from Core.di import (
    get_auth_repository,
    get_create_user_usecase,
    get_delete_user_usecase,
    get_login_user_usecase,
    get_mongodb_auth_repository,
    get_postgres_auth_repository,
    get_user_by_email_usecase,
    get_user_by_id_usecase,
)
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import AuthRepositoryPostgresSQl
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    DeleteUserUseCase,
    GetUserByEmailUseCase,
    GetUserByIdUseCase,
    LoginUserUseCase,
)


def test_get_postgres_auth_repository():
    repo = get_postgres_auth_repository()
    assert isinstance(repo, AuthRepositoryPostgresSQl)
    assert isinstance(repo, AuthRepository)


def test_get_mongodb_auth_repository():
    repo = get_mongodb_auth_repository()
    assert isinstance(repo, AuthRepositoryMongoDB)
    assert isinstance(repo, AuthRepository)


def test_get_auth_repository():
    postgres_repo = get_postgres_auth_repository()
    assert isinstance(get_auth_repository(postgres_repo), AuthRepository)


def test_get_auth_repository_postgresql():
    postgres_repo = get_postgres_auth_repository()
    assert isinstance(get_auth_repository(postgres_repo), AuthRepositoryPostgresSQl)


def test_get_auth_repository_mongodb():
    mongodb_repo = get_mongodb_auth_repository()
    assert isinstance(get_auth_repository(mongodb_repo), AuthRepositoryMongoDB)


def test_get_create_user_usecase():
    repo = get_postgres_auth_repository()
    usecase = get_create_user_usecase(repo=repo)
    assert isinstance(usecase, CreateUserUseCase)


def test_get_login_user_usecase():
    repo = get_postgres_auth_repository()
    usecase = get_login_user_usecase(repo=repo)
    assert isinstance(usecase, LoginUserUseCase)


def test_get_user_by_id_usecase():
    repo = get_postgres_auth_repository()
    usecase = get_user_by_id_usecase(repo=repo)
    assert isinstance(usecase, GetUserByIdUseCase)


def test_get_user_by_email_usecase():
    repo = get_postgres_auth_repository()
    usecase = get_user_by_email_usecase(repo=repo)
    assert isinstance(usecase, GetUserByEmailUseCase)


def test_get_delete_user_usecase():
    repo = get_postgres_auth_repository()
    usecase = get_delete_user_usecase(repo=repo)
    assert isinstance(usecase, DeleteUserUseCase)
