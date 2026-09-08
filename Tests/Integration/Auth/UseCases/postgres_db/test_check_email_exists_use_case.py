import pytest
from sqlalchemy.orm import Session
from Core.Session.session_pg import db_session
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import (
    AuthRepositoryPostgresSQl,
)
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases.CreateUserUseCase import CreateUserUseCase
from Features.Auth.Domain.UseCases.CheckEmailExistsUseCase import (
    CheckEmailExistsUseCase,
)
from Features.Auth.Domain.UseCases.DeleteUserUseCase import DeleteUserUseCase


@pytest.fixture
def auth_repository(db_session: Session) -> AuthRepository:
    return AuthRepositoryPostgresSQl(db=db_session)


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
    email = "pg_existing_email_check@test.com"

    # 1. إنشاء مستخدم بالإيميل المحدد
    user = await create_user_usecase.execute(
        email=email,
        name="Existing User",
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
    non_existent_email = "pg_non_existent_email_12345@test.com"

    # فحص إيميل غير مسجل مسبقاً ويجب أن يرجع False
    exists = await check_email_exists_usecase.execute(email=non_existent_email)
    assert exists is False


@pytest.mark.asyncio
async def test_check_email_exists_returns_false_after_user_deleted(
    create_user_usecase: CreateUserUseCase,
    check_email_exists_usecase: CheckEmailExistsUseCase,
    delete_user_usecase: DeleteUserUseCase,
):
    email = "pg_email_to_be_deleted@test.com"

    # 1. إنشاء المستخدم
    user = await create_user_usecase.execute(
        email=email,
        name="User To Delete",
        password="password123",
    )
    assert user is not None

    # 2. التأكد أن الإيميل موجود أولاً
    exists_before = await check_email_exists_usecase.execute(email=email)
    assert exists_before is True

    # 3. حذف المستخدم بواسطة Admin
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

    # 4. التحقق من أن فحص الإيميل بعد الحذف يرجع False
    exists_after = await check_email_exists_usecase.execute(email=email)
    assert exists_after is False


@pytest.mark.asyncio
async def test_check_email_exists_different_users(
    create_user_usecase: CreateUserUseCase,
    check_email_exists_usecase: CheckEmailExistsUseCase,
):
    email1 = "pg_multi_user1@test.com"
    email2 = "pg_multi_user2@test.com"
    unregistered_email = "pg_multi_unregistered@test.com"

    # إنشاء مستخدمين مختلفين
    await create_user_usecase.execute(
        email=email1,
        name="User One",
        password="password123",
    )
    await create_user_usecase.execute(
        email=email2,
        name="User Two",
        password="password123",
    )

    # التحقق من إيميل المستخدم الأول
    assert await check_email_exists_usecase.execute(email=email1) is True

    # التحقق من إيميل المستخدم الثاني
    assert await check_email_exists_usecase.execute(email=email2) is True

    # التحقق من إيميل غير مسجل
    assert await check_email_exists_usecase.execute(email=unregistered_email) is False
