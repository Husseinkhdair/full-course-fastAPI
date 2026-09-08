import pytest
from sqlalchemy.orm import Session
from Core.Session.session_pg import db_session
from Core.errors.AuthErrors import (
    InvalidEmailOrPassword,
    UserAlredyExists,
    UserDoesNotExists,
)
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import (
    AuthRepositoryPostgresSQl,
)
from Features.Auth.Domain.Entities.UserEntity import Role, Status, UserEntity


@pytest.fixture
def auth_repository(db_session: Session) -> AuthRepositoryPostgresSQl:
    """
    Fixture يربط المستودع بجلسة SQLAlchemy مزودة بـ Transaction Savepoint،
    بحيث يتم التراجع التلقائي (Rollback) بعد كل اختبار دون ترك أي بيانات في PostgreSQL.
    """
    return AuthRepositoryPostgresSQl(db=db_session)


# -------------------------------------------------------------
# 1. اختبارات إنشاء المستخدم (create_user)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_create_user_success_postgres(auth_repository: AuthRepositoryPostgresSQl):
    email = "pg_repo_create_success@test.com"
    name = "Postgres User"
    password = "password123"

    user = await auth_repository.create_user(email=email, name=name, password=password)

    assert user is not None
    assert isinstance(user, UserEntity)
    assert user.id is not None
    assert user.email == email
    assert user.name == name
    assert user.role == Role.USER.value or user.role == Role.USER
    assert user.status == Status.ACTIVE.value or user.status == Status.ACTIVE
    assert user.created_at is not None
    assert user.updated_at is not None


@pytest.mark.integration
async def test_create_user_with_role_admin_postgres(auth_repository: AuthRepositoryPostgresSQl):
    email = "pg_repo_create_admin@test.com"
    name = "Postgres Admin User"
    password = "password123"

    user = await auth_repository.create_user(
        email=email,
        name=name,
        password=password,
        role=Role.ADMIN,
    )

    assert user is not None
    assert user.role == Role.ADMIN.value or user.role == Role.ADMIN





@pytest.mark.integration
async def test_create_user_password_is_hashed_postgres(auth_repository: AuthRepositoryPostgresSQl):
    plain_pwd = "my_secret_password"
    user = await auth_repository.create_user(
        email="pg_repo_hashed_pwd@test.com",
        name="Security User",
        password=plain_pwd,
    )

    # كلمة المرور المخزنة في الكيان أو قاعدة البيانات لا يجب أن تطابق النص الصريح
    assert user.password != plain_pwd
    assert user.password.startswith("$2b$") or user.password.startswith("$2a$")


# -------------------------------------------------------------
# 2. اختبارات تسجيل الدخول (login_user)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_login_user_success_postgres(auth_repository: AuthRepositoryPostgresSQl):
    email = "pg_repo_login_success@test.com"
    password = "password123"

    await auth_repository.create_user(email=email, name="Login User", password=password)

    logged_user = await auth_repository.login_user(email=email, password=password)
    assert logged_user is not None
    assert logged_user.email == email


@pytest.mark.integration
async def test_login_user_wrong_password_postgres(auth_repository: AuthRepositoryPostgresSQl):
    email = "pg_repo_wrong_pwd@test.com"
    await auth_repository.create_user(email=email, name="User", password="password123")

    with pytest.raises(InvalidEmailOrPassword) as exc_info:
        await auth_repository.login_user(email=email, password="wrong_password_999")

    assert exc_info.value.status_code == 401


@pytest.mark.integration
async def test_login_user_not_found_postgres(auth_repository: AuthRepositoryPostgresSQl):
    with pytest.raises(InvalidEmailOrPassword) as exc_info:
        await auth_repository.login_user(
            email="non_existent_login@test.com",
            password="password123",
        )

    assert exc_info.value.status_code == 401


# -------------------------------------------------------------
# 3. اختبارات جلب المستخدم بالمعرف (get_user_by_id)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_get_user_by_id_success_postgres(auth_repository: AuthRepositoryPostgresSQl):
    user = await auth_repository.create_user(
        email="pg_repo_get_by_id@test.com",
        name="Target ID",
        password="password123",
    )

    fetched_user = await auth_repository.get_user_by_id(user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == user.email


@pytest.mark.integration
async def test_get_user_by_id_not_found_postgres(auth_repository: AuthRepositoryPostgresSQl):
    with pytest.raises(UserDoesNotExists) as exc_info:
        await auth_repository.get_user_by_id("non-existent-user-id-9999")

    assert exc_info.value.status_code == 400


# -------------------------------------------------------------
# 4. اختبارات جلب المستخدم بالبريد (get_user_by_email)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_get_user_by_email_success_postgres(auth_repository: AuthRepositoryPostgresSQl):
    email = "pg_repo_get_by_email@test.com"
    user = await auth_repository.create_user(
        email=email,
        name="Target Email",
        password="password123",
    )

    fetched_user = await auth_repository.get_user_by_email(email)
    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == email


@pytest.mark.integration
async def test_get_user_by_email_not_found_postgres(auth_repository: AuthRepositoryPostgresSQl):
    with pytest.raises(UserDoesNotExists) as exc_info:
        await auth_repository.get_user_by_email("non_existent_email_pg@test.com")

    assert exc_info.value.status_code == 400


# -------------------------------------------------------------
# 5. اختبارات فحص وجود البريد (check_email_exists)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_check_email_exists_postgres(auth_repository: AuthRepositoryPostgresSQl):
    email = "pg_repo_check_email@test.com"

    # قبل الإنشاء: يجب أن يرجع False
    exists_before = await auth_repository.check_email_exists(email)
    assert exists_before is False

    # بعد الإنشاء: يجب أن يرجع True
    await auth_repository.create_user(email=email, name="Check User", password="password123")
    exists_after = await auth_repository.check_email_exists(email)
    assert exists_after is True


# -------------------------------------------------------------
# 6. اختبارات حذف المستخدم (delete_user)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_delete_user_success_postgres(auth_repository: AuthRepositoryPostgresSQl):
    user = await auth_repository.create_user(
        email="pg_repo_delete_success@test.com",
        name="User To Delete",
        password="password123",
    )

    deleted = await auth_repository.delete_user(user.id)
    assert deleted is True

    # التأكد من أنه لم يعد موجوداً
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.integration
async def test_delete_user_not_found_postgres(auth_repository: AuthRepositoryPostgresSQl):
    with pytest.raises(UserDoesNotExists) as exc_info:
        await auth_repository.delete_user("non-existent-user-id-9999")

    assert exc_info.value.status_code == 400
