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
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.DeleteUserUseCase import DeleteUserUseCase


@pytest.fixture
async def auth_repository():
    async with get_clean_mongo_collection() as collection:
        yield AuthRepositoryMongoDB(collection=collection)


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return CreateUserUseCase(auth_repository=auth_repository)


@pytest.fixture
def delete_user_usecase(auth_repository: AuthRepository) -> DeleteUserUseCase:
    return DeleteUserUseCase(auth_repository=auth_repository)


@pytest.mark.asyncio
async def test_delete_user_by_admin_success(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
    auth_repository: AuthRepository,
):
    # 1. إنشاء مستخدم عادي لحذفه
    email = "mongo_delete_target_by_admin@test.com"
    user = await create_user_usecase.execute(
        email=email,
        name="Target User",
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

    # 3. تنفيذ الحذف
    result = await delete_user_usecase.execute(
        user_id=user.id,
        token=admin_token,
    )
    assert result is True

    # 4. التأكد من حذف المستخدم من MongoDB
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.asyncio
async def test_delete_user_by_superadmin_success(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
    auth_repository: AuthRepository,
):
    # 1. إنشاء مستخدم عادي
    email = "mongo_delete_target_by_superadmin@test.com"
    user = await create_user_usecase.execute(
        email=email,
        name="Target User 2",
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

    # 3. تنفيذ الحذف
    result = await delete_user_usecase.execute(
        user_id=user.id,
        token=superadmin_token,
    )
    assert result is True

    # 4. التأكد من الحذف
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.asyncio
async def test_delete_user_not_found(
    delete_user_usecase: DeleteUserUseCase,
):
    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # محاولة حذف معرّف غير موجود
    with pytest.raises(UserDoesNotExists) as exc_info:
        await delete_user_usecase.execute(
            user_id="non-existent-user-id-9999",
            token=admin_token,
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_user_cannot_delete_user(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
    auth_repository: AuthRepository,
):
    # 1. إنشاء مستخدم هدف
    email = "mongo_target_cannot_delete@test.com"
    target_user = await create_user_usecase.execute(
        email=email,
        name="Target User",
        password="password123",
    )

    # 2. توكن بمستوى صلاحية USER
    user_token = generate_token(
        payload=JWTPayload(
            id="normal-user-id",
            email="user@test.com",
            role=Role.USER.value,
        )
    )

    # 3. محاولة الحذف من مستخدم عادي يجب أن تفشل مع UserNotHaveRole (403)
    with pytest.raises(UserNotHaveRole) as exc_info:
        await delete_user_usecase.execute(
            user_id=target_user.id,
            token=user_token,
        )

    assert exc_info.value.status_code == 403

    # 4. التأكد أن المستخدم الهدف ما زال موجوداً
    existing_user = await auth_repository.get_user_by_id(target_user.id)
    assert existing_user is not None
    assert existing_user.id == target_user.id


@pytest.mark.asyncio
async def test_delete_user_without_token(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
):
    email = "mongo_target_no_token@test.com"
    target_user = await create_user_usecase.execute(
        email=email,
        name="Target User",
        password="password123",
    )

    # محاولة الحذف بدون توكن
    with pytest.raises(InvalidToken) as exc_info:
        await delete_user_usecase.execute(
            user_id=target_user.id,
            token=None,
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_with_invalid_token(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
):
    email = "mongo_target_invalid_token@test.com"
    target_user = await create_user_usecase.execute(
        email=email,
        name="Target User",
        password="password123",
    )

    # محاولة الحذف بتوكن تالف
    with pytest.raises(InvalidToken) as exc_info:
        await delete_user_usecase.execute(
            user_id=target_user.id,
            token="invalid.jwt.token",
        )

    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_delete_user_already_deleted_fails(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
):
    email = "mongo_target_double_delete@test.com"
    target_user = await create_user_usecase.execute(
        email=email,
        name="Target User",
        password="password123",
    )

    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # المرة الأولى: نجاح
    first_delete = await delete_user_usecase.execute(
        user_id=target_user.id,
        token=admin_token,
    )
    assert first_delete is True

    # المرة الثانية: فشل
    with pytest.raises(UserDoesNotExists) as exc_info:
        await delete_user_usecase.execute(
            user_id=target_user.id,
            token=admin_token,
        )

    assert exc_info.value.status_code == 400
