import pytest
from Core.Session.sessiong_mongos import get_clean_mongo_collection
from Core.errors.AuthErrors import InvalidEmailOrPassword
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import (
    AuthRepositoryMongoDB,
)
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.LoginUserUseCase import LoginUserUseCase


@pytest.fixture
async def auth_repository():
    async with get_clean_mongo_collection() as collection:
        yield AuthRepositoryMongoDB(collection=collection)


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return CreateUserUseCase(auth_repository=auth_repository)


@pytest.fixture
def login_user_usecase(auth_repository: AuthRepository) -> LoginUserUseCase:
    return LoginUserUseCase(auth_repository=auth_repository)


@pytest.mark.asyncio
async def test_login_user_use_case_success(
    create_user_usecase: CreateUserUseCase,
    login_user_usecase: LoginUserUseCase,
):
    email = "mongo_login_success@test.com"
    password = "password123"

    # 1. إنشاء المستخدم
    created_user = await create_user_usecase.execute(
        email=email,
        name="Mongo Login User",
        password=password,
    )
    assert created_user is not None

    # 2. تسجيل الدخول
    logged_user = await login_user_usecase.execute(
        email=email,
        password=password,
    )

    assert logged_user is not None
    assert isinstance(logged_user, UserEntity)
    assert logged_user.email == email
    assert logged_user.token is not None


@pytest.mark.asyncio
async def test_login_user_use_case_invalid_password(
    create_user_usecase: CreateUserUseCase,
    login_user_usecase: LoginUserUseCase,
):
    email = "mongo_wrong_pwd@test.com"
    correct_password = "password123"

    # 1. إنشاء المستخدم
    created_user = await create_user_usecase.execute(
        email=email,
        name="Mongo User",
        password=correct_password,
    )
    assert created_user is not None

    # 2. تسجيل الدخول بكلمة سر خاطئة
    with pytest.raises(InvalidEmailOrPassword):
        await login_user_usecase.execute(
            email=email,
            password="wrongpassword456",
        )


@pytest.mark.asyncio
async def test_login_user_use_case_user_not_found(
    login_user_usecase: LoginUserUseCase,
):
    # محاولة تسجيل الدخول لمستخدم غير موجود
    with pytest.raises(InvalidEmailOrPassword):
        await login_user_usecase.execute(
            email="nonexistent_mongo_user@test.com",
            password="password123",
        )
