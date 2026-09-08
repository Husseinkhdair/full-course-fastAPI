import pytest
from Core.Session.sessiong_mongos import get_clean_mongo_collection
from Core.errors.AuthErrors import (
    RoleError,
    UserAlredyExists,
)
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import (
    AuthRepositoryMongoDB,
)
from Features.Auth.Domain.Entities.UserEntity import Role, UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase


@pytest.fixture
async def auth_repository():
    async with get_clean_mongo_collection() as collection:
        yield AuthRepositoryMongoDB(collection=collection)


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return CreateUserUseCase(auth_repository=auth_repository)


@pytest.mark.asyncio
async def test_create_user_success(create_user_usecase: CreateUserUseCase):
    email = "mongo_success@test.com"
    name = "Mongo User"
    password = "password123"

    user = await create_user_usecase.execute(
        email=email,
        name=name,
        password=password,
    )

    assert user is not None
    assert isinstance(user, UserEntity)
    assert user.email == email
    assert user.name == name
    assert user.token is not None
    assert user.id is not None


@pytest.mark.asyncio
async def test_create_user_already_exists(create_user_usecase: CreateUserUseCase):
    email = "mongo_duplicate@test.com"
    name = "Duplicate User"
    password = "password123"

    # إنشاء المستخدم لأول مرة
    user = await create_user_usecase.execute(
        email=email,
        name=name,
        password=password,
    )
    assert user is not None

    # محاولة إنشاء نفس المستخدم مرة ثانية يجب أن ترمي خطأ UserAlredyExists
    with pytest.raises(UserAlredyExists):
        await create_user_usecase.execute(
            email=email,
            name=name,
            password=password,
        )


@pytest.mark.asyncio
async def test_create_admin_from_admin_success(
    create_user_usecase: CreateUserUseCase,
):
    email = "mongo_admin_create_admin@test.com"
    name = "Admin User"
    password = "password123"

    # توكن Admin المنشئ
    token = generate_token(
        payload=JWTPayload(
            id="test-admin-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
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
    email = "mongo_user_create_admin@test.com"
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
    email = "mongo_user_create_superadmin@test.com"
    name = "Super Admin"
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
            role=Role.SUPERADMIN,
            token=token,
        )

    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_superadmin_cannot_create_superadmin(
    create_user_usecase: CreateUserUseCase,
):
    email = "mongo_superadmin_create_superadmin@test.com"
    name = "Super Admin 2"
    password = "password123"

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
    email = "mongo_superadmin_create_admin@test.com"
    name = "New Admin"
    password = "password123"

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
    assert admin.role == Role.ADMIN.value
    assert admin.token is not None
