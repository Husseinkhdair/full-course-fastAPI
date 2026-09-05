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

