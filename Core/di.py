from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import AuthRepositoryPostgresSQl
from fastapi import Depends
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase,
    DeleteUserUseCase
)

# -----------------------------
# Repositories Dependency Providers
# -----------------------------
def get_postgres_auth_repository() -> AuthRepository:
    return AuthRepositoryPostgresSQl()

def get_mongodb_auth_repository() -> AuthRepository:
    return AuthRepositoryMongoDB()

def get_auth_repository(repo: AuthRepository = Depends(get_postgres_auth_repository)) -> AuthRepository:
    return repo

# -----------------------------
# Auth UseCases Dependency Providers
# -----------------------------
def get_create_user_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> CreateUserUseCase:
    return CreateUserUseCase(repo)

def get_login_user_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> LoginUserUseCase:
    return LoginUserUseCase(repo)

def get_user_by_id_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> GetUserByIdUseCase:
    return GetUserByIdUseCase(repo)

def get_user_by_email_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> GetUserByEmailUseCase:
    return GetUserByEmailUseCase(repo)

def get_delete_user_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> DeleteUserUseCase:
    return DeleteUserUseCase(repo)

