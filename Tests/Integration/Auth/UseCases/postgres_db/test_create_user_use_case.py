from Core.errors.AuthErrors import RoleError
from Features.Auth.Domain.Entities.UserEntity import Role
from Core.security.Jwt import JWTPayload
from Core.security.Jwt import generate_token
import pytest
from sqlalchemy.orm import Session
from Core.errors.AuthErrors import UserAlredyExists
from Core.Session.session_pg import db_session
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import (
    AuthRepositoryPostgresSQl,
)
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase


@pytest.fixture
def auth_repository(db_session: Session) -> AuthRepository:
    return AuthRepositoryPostgresSQl(db=db_session)


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return CreateUserUseCase(auth_repository=auth_repository)


@pytest.mark.asyncio
async def test_create_user_success(create_user_usecase: CreateUserUseCase):
    email = "pg_rollback_success@test.com"
    name = "Postgres User"
    password = "password123"

    user = await create_user_usecase.execute(
        email=email,
        name=name,
        password=password
    )

    assert user is not None
    assert isinstance(user, UserEntity)
    assert user.email == email
    assert user.name == name
    assert user.token is not None
    assert user.id is not None


@pytest.mark.asyncio
async def test_create_user_already_exists(create_user_usecase: CreateUserUseCase):
    email = "pg_rollback_duplicate@test.com"
    name = "Duplicate User"
    password = "password123"

    # إنشاء المستخدم لأول مرة
    user = await create_user_usecase.execute(
        email=email,
        name=name,
        password=password
    )
    assert user is not None

    # محاولة إنشاء نفس المستخدم مرة ثانية يجب أن ترمي خطأ UserAlredyExists
    with pytest.raises(UserAlredyExists):
        await create_user_usecase.execute(
            email=email,
            name=name,
            password=password
        )

@pytest.mark.asyncio
async def test_create_admin_from_admin_success(
    create_user_usecase: CreateUserUseCase,
):
    email = "pg_rollback_admin@test.com"
    name = "Admin User"
    password = "password123"

    # Token of the admin who is creating the new user
    token = generate_token(
        payload=JWTPayload(
            id="test-admin-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )

    # Admin creates another Admin
    admin = await create_user_usecase.execute(
        email=email,
        name=name,
        password=password,
        role=Role.ADMIN,
        token=token,
    )

    assert admin is not None
    assert isinstance(admin, UserEntity)

    assert admin.id is not None
    assert admin.email == email
    assert admin.name == name

    assert admin.role == Role.ADMIN.value
    assert admin.token is not None


@pytest.mark.asyncio
async def test_user_cannot_create_admin(
    create_user_usecase: CreateUserUseCase,
):
    email = "pg_user_create_admin@test.com"
    name = "Admin User"
    password = "password123"

    token = generate_token(
        payload=JWTPayload(
            id="test-user-id",
            email="user@test.com",
            role=Role.USER.value,
        )
    )

    with pytest.raises(RoleError) as exc_info:
        await create_user_usecase.execute(
            email=email,
            name=name,
            password=password,
            role=Role.ADMIN,
            token=token,
        )

    assert exc_info.value.status_code == 403

@pytest.mark.asyncio
async def test_user_cannot_create_superadmin(
    create_user_usecase: CreateUserUseCase,
):
    email = "pg_user_create_superadmin@test.com"
    name = "Super Admin"
    password = "password123"

    # Token belongs to normal USER
    token = generate_token(
        payload=JWTPayload(
            id="test-user-id",
            email="user@test.com",
            role=Role.USER.value,
        )
    )

    with pytest.raises(RoleError) as exc_info:
        await create_user_usecase.execute(
            email=email,
            name=name,
            password=password,
            role=Role.SUPERADMIN,
            token=token,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_superadmin_cannot_create_superadmin(
    create_user_usecase: CreateUserUseCase,
):
    email = "pg_superadmin_create_superadmin@test.com"
    name = "Super Admin 2"
    password = "password123"

    # Token belongs to SUPERADMIN
    token = generate_token(
        payload=JWTPayload(
            id="test-superadmin-id",
            email="superadmin@test.com",
            role=Role.SUPERADMIN.value,
        )
    )

    with pytest.raises(RoleError) as exc_info:
        await create_user_usecase.execute(
            email=email,
            name=name,
            password=password,
            role=Role.SUPERADMIN,
            token=token,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_superadmin_create_admin_success(
    create_user_usecase: CreateUserUseCase,
):
    email = "pg_superadmin_create_admin@test.com"
    name = "New Admin"
    password = "password123"

    # Token belongs to SUPERADMIN
    token = generate_token(
        payload=JWTPayload(
            id="test-superadmin-id",
            email="superadmin@test.com",
            role=Role.SUPERADMIN.value,
        )
    )

    admin = await create_user_usecase.execute(
        email=email,
        name=name,
        password=password,
        role=Role.ADMIN,
        token=token,
    )

    assert admin is not None
    assert admin.id is not None

    assert admin.email == email
    assert admin.name == name

    # إذا UserEntity يرجع role كـ string
    assert admin.role == Role.ADMIN.value

    assert admin.token is not None