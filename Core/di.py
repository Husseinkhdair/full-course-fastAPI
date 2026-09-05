from fastapi import Depends
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase
)

# -----------------------------
# Repositories Dependency Providers
# -----------------------------
def get_auth_repository() -> AuthRepository:
    return AuthRepositoryMongoDB()


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
