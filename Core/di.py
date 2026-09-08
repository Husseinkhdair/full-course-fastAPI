from Core.errors.AuthErrors import TokenIsRequire
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from fastapi import Depends, Header, Cookie, Request
from fastapi.params import Depends as DependsParam
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import AuthRepositoryPostgresSQl
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase,
    DeleteUserUseCase,
    CheckEmailExistsUseCase
)
from Features.Post.Domain.Repository.PostRepository import PostRepository
from Features.Post.Data.DataSources.PostRepositoryPostgresSQL import PostRepositoryPostgresSQL
from Features.Post.Data.DataSources.PostRepositoryMongoDB import PostRepositoryMongoDB
from Features.Post.Domain.UseCases import (
    CreatePostUseCase,
    UpdatePostUseCase,
    DeletePostUseCase,
    GetPostByIdUseCase,
    ListPostsUseCase
)
from Core.errors.AuthErrors import InvalidToken

# -----------------------------
# Security & Token Providers
# -----------------------------
security = HTTPBearer(auto_error=False)


def get_current_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    token = None

    # 1. من Swagger Authorize (Authorization: Bearer <token>)
    if credentials:
        token = credentials.credentials

    # 2. من الـ Header مباشرة (access_token أو access-token أو authorization)
    if not token:
        raw_header = (
            request.headers.get("access_token")
            or request.headers.get("access-token")
            or request.headers.get("authorization")
        )
        if raw_header:
            token = raw_header[7:].strip() if raw_header.startswith("Bearer ") else raw_header.strip()

    # 3. خيار احتياطي من الـ Cookie
    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise TokenIsRequire()

    return token
# -----------------------------
# Repositories Dependency Providers
# -----------------------------
def get_postgres_auth_repository() -> AuthRepository:
    return AuthRepositoryPostgresSQl()

def get_mongodb_auth_repository() -> AuthRepository:
    return AuthRepositoryMongoDB()

def get_auth_repository(repo: AuthRepository = Depends(get_postgres_auth_repository)) -> AuthRepository:
    if isinstance(repo, DependsParam) or repo is None:
        return get_postgres_auth_repository()
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

def get_check_email_exists_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> CheckEmailExistsUseCase:
    return CheckEmailExistsUseCase(repo)


# -----------------------------
# Post Repositories Dependency Providers
# -----------------------------
def get_postgres_post_repository() -> PostRepository:
    return PostRepositoryPostgresSQL()

def get_mongodb_post_repository() -> PostRepository:
    return PostRepositoryMongoDB()

def get_post_repository(repo: PostRepository = Depends(get_postgres_post_repository)) -> PostRepository:
    if isinstance(repo, DependsParam) or repo is None:
        return get_postgres_post_repository()
    return repo


# -----------------------------
# Delete User with Cascade Post Deletion
# -----------------------------
def get_delete_user_usecase(
    repo: AuthRepository = Depends(get_auth_repository),
    post_repo: PostRepository = Depends(get_post_repository),
) -> DeleteUserUseCase:
    return DeleteUserUseCase(auth_repository=repo, post_repository=post_repo)


# -----------------------------
# Post UseCases Dependency Providers
# -----------------------------
def get_create_post_usecase(
    repo: PostRepository = Depends(get_post_repository),
    auth_repo: AuthRepository = Depends(get_auth_repository),
) -> CreatePostUseCase:
    return CreatePostUseCase(post_repository=repo, auth_repository=auth_repo)

def get_update_post_usecase(
    repo: PostRepository = Depends(get_post_repository),
    auth_repo: AuthRepository = Depends(get_auth_repository),
) -> UpdatePostUseCase:
    return UpdatePostUseCase(post_repository=repo, auth_repository=auth_repo)

def get_delete_post_usecase(
    repo: PostRepository = Depends(get_post_repository),
    auth_repo: AuthRepository = Depends(get_auth_repository),
) -> DeletePostUseCase:
    return DeletePostUseCase(post_repository=repo, auth_repository=auth_repo)

def get_post_by_id_usecase(
    repo: PostRepository = Depends(get_post_repository)
) -> GetPostByIdUseCase:
    return GetPostByIdUseCase(repo)

def get_list_posts_usecase(
    repo: PostRepository = Depends(get_post_repository)
) -> ListPostsUseCase:
    return ListPostsUseCase(repo)



