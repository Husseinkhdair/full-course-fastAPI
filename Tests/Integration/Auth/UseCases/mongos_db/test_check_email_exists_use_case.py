import pytest
from Core.Session.sessiong_mongos import get_clean_mongo_collection
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import (
    AuthRepositoryMongoDB,
)
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.CheckEmailExistsUseCase import (
    CheckEmailExistsUseCase,
)
from Features.Auth.Domain.UseCases.DeleteUserUseCase import DeleteUserUseCase


@pytest.fixture
async def auth_repository():
    async with get_clean_mongo_collection() as collection:
        yield AuthRepositoryMongoDB(collection=collection)


@pytest.fixture
def create_user_usecase(auth_repository: AuthRepository) -> CreateUserUseCase:
    return CreateUserUseCase(auth_repository=auth_repository)


@pytest.fixture
def check_email_exists_usecase(
    auth_repository: AuthRepository,
) -> CheckEmailExistsUseCase:
    return CheckEmailExistsUseCase(auth_repository=auth_repository)


@pytest.fixture
def delete_user_usecase(auth_repository: AuthRepository) -> DeleteUserUseCase:
    return DeleteUserUseCase(auth_repository=auth_repository)


@pytest.mark.asyncio
async def test_check_email_exists_returns_true_when_user_exists(
    create_user_usecase: CreateUserUseCase,
    check_email_exists_usecase: CheckEmailExistsUseCase,
):
    email = "mongo_existing_email_check@test.com"

    # 1. إنشاء مستخدم بالإيميل
    user = await create_user_usecase.execute(
        email=email,
        name="Existing Mongo User",
        password="password123",
    )
    assert user is not None

    # 2. فحص وجود الإيميل ويجب أن يرجع True
    exists = await check_email_exists_usecase.execute(email=email)
    assert exists is True


@pytest.mark.asyncio
async def test_check_email_exists_returns_false_when_user_does_not_exist(
    check_email_exists_usecase: CheckEmailExistsUseCase,
):
    non_existent_email = "mongo_non_existent_email_12345@test.com"

    # فحص إيميل غير مسجل
    exists = await check_email_exists_usecase.execute(email=non_existent_email)
    assert exists is False


@pytest.mark.asyncio
async def test_check_email_exists_returns_false_after_user_deleted(
    create_user_usecase: CreateUserUseCase,
    check_email_exists_usecase: CheckEmailExistsUseCase,
    delete_user_usecase: DeleteUserUseCase,
):
    email = "mongo_email_to_be_deleted@test.com"

    # 1. إنشاء المستخدم
    user = await create_user_usecase.execute(
        email=email,
        name="User To Delete",
        password="password123",
    )
    assert user is not None

    # 2. التأكد أن الإيميل موجود
    exists_before = await check_email_exists_usecase.execute(email=email)
    assert exists_before is True

    # 3. حذف المستخدم
    admin_token = generate_token(
        payload=JWTPayload(
            id="admin-id",
            email="admin@test.com",
            role=Role.ADMIN.value,
        )
    )
    deleted = await delete_user_usecase.execute(
        user_id=user.id,
        token=admin_token,
    )
    assert deleted is True

    # 4. التأكد من أن الفحص يرجع False
    exists_after = await check_email_exists_usecase.execute(email=email)
    assert exists_after is False


@pytest.mark.asyncio
async def test_check_email_exists_different_users(
    create_user_usecase: CreateUserUseCase,
    check_email_exists_usecase: CheckEmailExistsUseCase,
):
    email1 = "mongo_multi_user1@test.com"
    email2 = "mongo_multi_user2@test.com"
    unregistered_email = "mongo_multi_unregistered@test.com"

    await create_user_usecase.execute(
        email=email1,
        name="Mongo User One",
        password="password123",
    )
    await create_user_usecase.execute(
        email=email2,
        name="Mongo User Two",
        password="password123",
    )

    assert await check_email_exists_usecase.execute(email=email1) is True
    assert await check_email_exists_usecase.execute(email=email2) is True
    assert await check_email_exists_usecase.execute(email=unregistered_email) is False
