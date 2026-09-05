from Features.Auth.Domain.UseCases import DeleteUserUseCase
from Core.di import get_delete_user_usecase
from Features.Auth.Domain.UseCases import GetUserByEmailUseCase
from Core.di import get_user_by_email_usecase
from Features.Auth.Domain.UseCases import GetUserByIdUseCase
from Core.di import get_user_by_id_usecase
from Features.Auth.Domain.UseCases import LoginUserUseCase
from Core.di import get_login_user_usecase
from Features.Auth.Domain.UseCases import CreateUserUseCase
from Core.di import get_create_user_usecase
from Core.di import get_auth_repository, get_mongodb_auth_repository, get_postgres_auth_repository
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Data.DataSources.AuthRepositoryPostgreSQL import AuthRepositoryPostgreSQL
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB

def test_get_auth_repository():
    assert isinstance(get_auth_repository(get_postgres_auth_repository()), AuthRepository)

def test_get_auth_repository_postgresql():
    assert isinstance(get_auth_repository(get_postgres_auth_repository()), AuthRepositoryPostgreSQL)

def test_get_auth_repository_mongodb():
    assert isinstance(get_auth_repository(get_mongodb_auth_repository()), AuthRepositoryMongoDB)


def test_get_create_user_usecase():
    assert isinstance(get_create_user_usecase(), CreateUserUseCase)

def test_get_login_user_usecase():
    assert isinstance(get_login_user_usecase(), LoginUserUseCase)

def test_get_user_by_id_usecase():
    assert isinstance(get_user_by_id_usecase(), GetUserByIdUseCase)

def test_get_user_by_email_usecase():
    assert isinstance(get_user_by_email_usecase(), GetUserByEmailUseCase)

def test_get_delete_user_usecase():
    assert isinstance(get_delete_user_usecase(), DeleteUserUseCase)
