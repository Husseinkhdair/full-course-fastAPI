import pytest
from sqlalchemy.orm import Session
from Core.Session.session_pg import db_session
from Core.errors.AuthErrors import (
    UserDoesNotExists,
    UserNotHaveRole,
    InvalidToken,
    RoleError,
)
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import (
    AuthRepositoryPostgresSQl,
)
from Features.Auth.Domain.Entities.UserEntity import Role, UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.DeleteUserUseCase import DeleteUserUseCase


@pytest.fixture
def auth_repository(db_session: Session) -> AuthRepository:
    return AuthRepositoryPostgresSQl(db=db_session)


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
    email = "pg_delete_target_by_admin@test.com"
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

    # 3. تنفيذ عملية الحذف بواسطة ADMIN
    result = await delete_user_usecase.execute(
        user_id=user.id,
        token=admin_token,
    )
    assert result is True

    # 4. التأكد من أن المستخدم لم يعد موجوداً في قاعدة البيانات
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.asyncio
async def test_delete_user_by_superadmin_success(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
    auth_repository: AuthRepository,
):
    # 1. إنشاء مستخدم عادي
    email = "pg_delete_target_by_superadmin@test.com"
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

    # 3. تنفيذ عملية الحذف بواسطة SUPERADMIN
    result = await delete_user_usecase.execute(
        user_id=user.id,
        token=superadmin_token,
    )
    assert result is True

    # 4. التأكد من حذف المستخدم
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.asyncio
async def test_delete_user_not_found(
    delete_user_usecase: DeleteUserUseCase,
):
    # توكن Admin
    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # محاولة حذف معرّف غير موجود في قاعدة البيانات
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
    email = "pg_target_cannot_delete@test.com"
    target_user = await create_user_usecase.execute(
        email=email,
        name="Target User",
        password="password123",
    )

    # 2. توكن بمستوى صلاحية USER عادي
    user_token = generate_token(
        payload=JWTPayload(
            id="normal-user-id",
            email="user@test.com",
            role=Role.USER.value,
        )
    )

    # 3. محاولة الحذف بمستخدم عادي يجب أن تفشل مع UserNotHaveRole (403)
    with pytest.raises(UserNotHaveRole) as exc_info:
        await delete_user_usecase.execute(
            user_id=target_user.id,
            token=user_token,
        )

    assert exc_info.value.status_code == 403

    # 4. التأكد أن المستخدم الهدف ما زال موجوداً ولم يُحذف
    existing_user = await auth_repository.get_user_by_id(target_user.id)
    assert existing_user is not None
    assert existing_user.id == target_user.id


@pytest.mark.asyncio
async def test_delete_user_without_token(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
):
    email = "pg_target_no_token@test.com"
    target_user = await create_user_usecase.execute(
        email=email,
        name="Target User",
        password="password123",
    )

    # محاولة الحذف بتمرير token=None
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
    email = "pg_target_invalid_token@test.com"
    target_user = await create_user_usecase.execute(
        email=email,
        name="Target User",
        password="password123",
    )

    # محاولة الحذف بتوكن عشوائي غير صالح
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
    email = "pg_target_double_delete@test.com"
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

    # المرة الأولى: نجاح الحذف
    first_delete = await delete_user_usecase.execute(
        user_id=target_user.id,
        token=admin_token,
    )
    assert first_delete is True

    # المرة الثانية: محاولة حذف نفس المستخدم مرة أخرى يجب أن ترمي خطأ UserDoesNotExists (400)
    with pytest.raises(UserDoesNotExists) as exc_info:
        await delete_user_usecase.execute(
            user_id=target_user.id,
            token=admin_token,
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_admin_cannot_delete_another_admin(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
    auth_repository: AuthRepository,
):
    # 1. إنشاء مستخدم بصلاحية ADMIN بواسطة SuperAdmin
    superadmin_token = generate_token(
        payload=JWTPayload(
            id="superadmin-creator-id",
            email="superadmin@test.com",
            role=Role.SUPERADMIN.value,
        )
    )
    target_admin = await create_user_usecase.execute(
        email="target_admin_delete@test.com",
        name="Target Admin",
        password="password123",
        role=Role.ADMIN,
        token=superadmin_token,
    )
    assert target_admin is not None

    # 2. إنشاء توكن لمشرف عادي ADMIN
    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-executor-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # 3. محاولة المشرف حذف مشرف آخر يجب أن تُرفض مع RoleError (403)
    with pytest.raises(RoleError) as exc_info:
        await delete_user_usecase.execute(
            user_id=target_admin.id,
            token=admin_token,
        )

    assert exc_info.value.status_code == 403
    assert "admin cannot delete" in exc_info.value.detail.lower()

    # 4. التأكد من أن المشرف الهدف لم يُحذف وما زال موجوداً
    existing_admin = await auth_repository.get_user_by_id(target_admin.id)
    assert existing_admin is not None
    assert existing_admin.id == target_admin.id


@pytest.mark.asyncio
async def test_superadmin_can_delete_admin(
    create_user_usecase: CreateUserUseCase,
    delete_user_usecase: DeleteUserUseCase,
    auth_repository: AuthRepository,
):
    # 1. إنشاء مستخدم بصلاحية ADMIN
    superadmin_token = generate_token(
        payload=JWTPayload(
            id="superadmin-creator-id",
            email="superadmin@test.com",
            role=Role.SUPERADMIN.value,
        )
    )
    target_admin = await create_user_usecase.execute(
        email="target_admin_to_del_by_super@test.com",
        name="Target Admin",
        password="password123",
        role=Role.ADMIN,
        token=superadmin_token,
    )
    assert target_admin is not None

    # 2. تنفيذ الحذف بواسطة SUPERADMIN ويجب أن ينجح
    result = await delete_user_usecase.execute(
        user_id=target_admin.id,
        token=superadmin_token,
    )
    assert result is True

    # 3. التأكد من حذفه فعلياً من قاعدة البيانات
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(target_admin.id)

