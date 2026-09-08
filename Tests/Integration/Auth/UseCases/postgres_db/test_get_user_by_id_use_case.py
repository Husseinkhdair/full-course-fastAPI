import pytest
from sqlalchemy.orm import Session
from Core.Session.session_pg import db_session
from Core.errors.AuthErrors import (
    UserDoesNotExists,
    UserNotHaveRole,
    InvalidToken,
)
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import (
    AuthRepositoryPostgresSQl,
)
from Features.Auth.Domain.Entities.UserEntity import Role, UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.GetUserByIdUseCase import GetUserByIdUseCase


@pytest.fixture
def auth_repository(db_session: Session) -> AuthRepository:
    return AuthRepositoryPostgresSQl(db=db_session)


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return CreateUserUseCase(auth_repository=auth_repository)


@pytest.fixture
def get_user_by_id_usecase(
    auth_repository: AuthRepository,
) -> GetUserByIdUseCase:
    return GetUserByIdUseCase(auth_repository=auth_repository)


@pytest.mark.asyncio
async def test_get_user_by_id_by_admin_success(
    create_user_usecase: CreateUserUseCase,
    get_user_by_id_usecase: GetUserByIdUseCase,
):
    # 1. إنشاء مستخدم هدف
    email = "pg_get_by_id_admin@test.com"
    name = "Target By ID Admin"
    user = await create_user_usecase.execute(
        email=email,
        name=name,
        password="password123",
    )
    assert user is not None
    assert user.id is not None

    # 2. إنشاء توكن بصلاحية ADMIN
    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-executor-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # 3. جلب المستخدم بواسطة ADMIN
    fetched_user = await get_user_by_id_usecase.execute(
        user_id=user.id,
        token=admin_token,
    )

    assert fetched_user is not None
    assert isinstance(fetched_user, UserEntity)
    assert fetched_user.id == user.id
    assert fetched_user.email == email
    assert fetched_user.name == name


@pytest.mark.asyncio
async def test_get_user_by_id_by_superadmin_success(
    create_user_usecase: CreateUserUseCase,
    get_user_by_id_usecase: GetUserByIdUseCase,
):
    # 1. إنشاء مستخدم هدف
    email = "pg_get_by_id_superadmin@test.com"
    user = await create_user_usecase.execute(
        email=email,
        name="Target By ID SuperAdmin",
        password="password123",
    )
    assert user is not None

    # 2. إنشاء توكن بصلاحية SUPERADMIN
    superadmin_token = generate_token(
        payload=JWTPayload(
            id="superadmin-executor-id",
            email="superadmin@test.com",
            role=Role.SUPERADMIN.value,
        )
    )

    # 3. جلب المستخدم بواسطة SUPERADMIN
    fetched_user = await get_user_by_id_usecase.execute(
        user_id=user.id,
        token=superadmin_token,
    )

    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == email


@pytest.mark.asyncio
async def test_get_user_by_id_user_forbidden(
    create_user_usecase: CreateUserUseCase,
    get_user_by_id_usecase: GetUserByIdUseCase,
):
    # 1. إنشاء مستخدم هدف
    email = "pg_get_by_id_forbidden@test.com"
    user = await create_user_usecase.execute(
        email=email,
        name="Target Forbidden",
        password="password123",
    )

    # 2. توكن بمستوى مستخدم عادي USER
    user_token = generate_token(
        payload=JWTPayload(
            id="user-executor-id",
            email="user@test.com",
            role=Role.USER.value,
        )
    )

    # 3. محاولة جلب المستخدم بمستخدم عادي يجب أن تفشل مع UserNotHaveRole (403)
    with pytest.raises(UserNotHaveRole) as exc_info:
        await get_user_by_id_usecase.execute(
            user_id=user.id,
            token=user_token,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    get_user_by_id_usecase: GetUserByIdUseCase,
):
    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # البحث عن معرّف غير موجود يجب أن يرمي UserDoesNotExists (400)
    with pytest.raises(UserDoesNotExists) as exc_info:
        await get_user_by_id_usecase.execute(
            user_id="non-existent-user-id-9999",
            token=admin_token,
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_user_by_id_without_token(
    create_user_usecase: CreateUserUseCase,
    get_user_by_id_usecase: GetUserByIdUseCase,
):
    email = "pg_get_by_id_no_token@test.com"
    user = await create_user_usecase.execute(
        email=email,
        name="User No Token",
        password="password123",
    )

    # استدعاء بدون توكن (None) يجب أن يرمي InvalidToken (401)
    with pytest.raises(InvalidToken) as exc_info:
        await get_user_by_id_usecase.execute(
            user_id=user.id,
            token=None,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_id_with_invalid_token(
    create_user_usecase: CreateUserUseCase,
    get_user_by_id_usecase: GetUserByIdUseCase,
):
    email = "pg_get_by_id_invalid_token@test.com"
    user = await create_user_usecase.execute(
        email=email,
        name="User Invalid Token",
        password="password123",
    )

    # استدعاء بتوكن غير صالح يجب أن يرمي InvalidToken (401)
    with pytest.raises(InvalidToken) as exc_info:
        await get_user_by_id_usecase.execute(
            user_id=user.id,
            token="invalid.jwt.token",
        )

    assert exc_info.value.status_code == 401
