import pytest
from Core.Session.sessiong_mongos import get_clean_mongo_collection
from Core.errors.AuthErrors import (
    UserDoesNotExists,
    UserNotHaveRole,
    InvalidToken,
)
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import (
    AuthRepositoryMongoDB,
)
from Features.Auth.Domain.Entities.UserEntity import Role, UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.GetUserByEmailUseCase import (
    GetUserByEmailUseCase,
)


@pytest.fixture
async def auth_repository():
    async with get_clean_mongo_collection() as collection:
        yield AuthRepositoryMongoDB(collection=collection)


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return CreateUserUseCase(auth_repository=auth_repository)


@pytest.fixture
def get_user_by_email_usecase(
    auth_repository: AuthRepository,
) -> GetUserByEmailUseCase:
    return GetUserByEmailUseCase(auth_repository=auth_repository)


@pytest.mark.asyncio
async def test_get_user_by_email_by_admin_success(
    create_user_usecase: CreateUserUseCase,
    get_user_by_email_usecase: GetUserByEmailUseCase,
):
    # 1. إنشاء مستخدم هدف
    email = "mongo_get_by_email_admin@test.com"
    name = "Target By Email Admin"
    user = await create_user_usecase.execute(
        email=email,
        name=name,
        password="password123",
    )
    assert user is not None

    # 2. إنشاء توكن بصلاحية ADMIN
    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-executor-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # 3. جلب المستخدم بواسطة ADMIN عبر الإيميل
    fetched_user = await get_user_by_email_usecase.execute(
        email=email,
        token=admin_token,
    )

    assert fetched_user is not None
    assert isinstance(fetched_user, UserEntity)
    assert fetched_user.id == user.id
    assert fetched_user.email == email
    assert fetched_user.name == name


@pytest.mark.asyncio
async def test_get_user_by_email_by_superadmin_success(
    create_user_usecase: CreateUserUseCase,
    get_user_by_email_usecase: GetUserByEmailUseCase,
):
    # 1. إنشاء مستخدم هدف
    email = "mongo_get_by_email_superadmin@test.com"
    user = await create_user_usecase.execute(
        email=email,
        name="Target By Email SuperAdmin",
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

    # 3. جلب المستخدم بواسطة SUPERADMIN عبر الإيميل
    fetched_user = await get_user_by_email_usecase.execute(
        email=email,
        token=superadmin_token,
    )

    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == email


@pytest.mark.asyncio
async def test_get_user_by_email_user_forbidden(
    create_user_usecase: CreateUserUseCase,
    get_user_by_email_usecase: GetUserByEmailUseCase,
):
    # 1. إنشاء مستخدم هدف
    email = "mongo_get_by_email_forbidden@test.com"
    await create_user_usecase.execute(
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
        await get_user_by_email_usecase.execute(
            email=email,
            token=user_token,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(
    get_user_by_email_usecase: GetUserByEmailUseCase,
):
    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # البحث عن إيميل غير مسجل يجب أن يرمي UserDoesNotExists (400)
    with pytest.raises(UserDoesNotExists) as exc_info:
        await get_user_by_email_usecase.execute(
            email="non_existent_mongo_email_123@test.com",
            token=admin_token,
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_get_user_by_email_without_token(
    create_user_usecase: CreateUserUseCase,
    get_user_by_email_usecase: GetUserByEmailUseCase,
):
    email = "mongo_get_by_email_no_token@test.com"
    await create_user_usecase.execute(
        email=email,
        name="User No Token",
        password="password123",
    )

    # استدعاء بدون توكن (None) يجب أن يرمي InvalidToken (401)
    with pytest.raises(InvalidToken) as exc_info:
        await get_user_by_email_usecase.execute(
            email=email,
            token=None,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_email_with_invalid_token(
    create_user_usecase: CreateUserUseCase,
    get_user_by_email_usecase: GetUserByEmailUseCase,
):
    email = "mongo_get_by_email_invalid_token@test.com"
    await create_user_usecase.execute(
        email=email,
        name="User Invalid Token",
        password="password123",
    )

    # استدعاء بتوكن غير صالح يجب أن يرمي InvalidToken (401)
    with pytest.raises(InvalidToken) as exc_info:
        await get_user_by_email_usecase.execute(
            email=email,
            token="invalid.jwt.token",
        )

    assert exc_info.value.status_code == 401
