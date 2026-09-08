import pytest
from Core.Session.sessiong_mongos import get_clean_mongo_collection
from Core.errors.AuthErrors import (
    InvalidEmailOrPassword,
    UserAlredyExists,
    UserDoesNotExists,
)
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import (
    AuthRepositoryMongoDB,
)
from Features.Auth.Domain.Entities.UserEntity import Role, Status, UserEntity


@pytest.fixture
async def auth_repository():
    """
    Fixture يربط المستودع بـ Collection مستقلة،
    وعند انتهاء الاختبار يتم مسح وحذف كافة البيانات المدخلة تلقائياً (Rollback/Cleanup)
    عبر get_clean_mongo_collection لضمان بيئة نظيفة ومعزولة تماماً في MongoDB.
    """
    async with get_clean_mongo_collection() as collection:
        yield AuthRepositoryMongoDB(collection=collection)


# -------------------------------------------------------------
# 1. اختبارات إنشاء المستخدم في MongoDB (create_user)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_create_user_success_mongo(auth_repository: AuthRepositoryMongoDB):
    email = "mongo_repo_create_success@test.com"
    name = "Mongo User"
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
async def test_create_user_with_role_admin_mongo(auth_repository: AuthRepositoryMongoDB):
    email = "mongo_repo_create_admin@test.com"
    name = "Mongo Admin User"
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
async def test_create_user_password_is_hashed_mongo(auth_repository: AuthRepositoryMongoDB):
    plain_pwd = "my_secret_mongo_password"
    user = await auth_repository.create_user(
        email="mongo_repo_hashed_pwd@test.com",
        name="Security Mongo User",
        password=plain_pwd,
    )

    assert user.password != plain_pwd
    assert user.password.startswith("$2b$") or user.password.startswith("$2a$")


# -------------------------------------------------------------
# 2. اختبارات تسجيل الدخول في MongoDB (login_user)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_login_user_success_mongo(auth_repository: AuthRepositoryMongoDB):
    email = "mongo_repo_login_success@test.com"
    password = "password123"

    await auth_repository.create_user(email=email, name="Login User", password=password)

    logged_user = await auth_repository.login_user(email=email, password=password)
    assert logged_user is not None
    assert logged_user.email == email


@pytest.mark.integration
async def test_login_user_wrong_password_mongo(auth_repository: AuthRepositoryMongoDB):
    email = "mongo_repo_wrong_pwd@test.com"
    await auth_repository.create_user(email=email, name="User", password="password123")

    with pytest.raises(InvalidEmailOrPassword) as exc_info:
        await auth_repository.login_user(email=email, password="wrong_password_999")

    assert exc_info.value.status_code == 401


@pytest.mark.integration
async def test_login_user_not_found_mongo(auth_repository: AuthRepositoryMongoDB):
    with pytest.raises(InvalidEmailOrPassword) as exc_info:
        await auth_repository.login_user(
            email="non_existent_mongo_login@test.com",
            password="password123",
        )

    assert exc_info.value.status_code == 401


# -------------------------------------------------------------
# 3. اختبارات جلب المستخدم بالمعرف في MongoDB (get_user_by_id)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_get_user_by_id_success_mongo(auth_repository: AuthRepositoryMongoDB):
    user = await auth_repository.create_user(
        email="mongo_repo_get_by_id@test.com",
        name="Target ID",
        password="password123",
    )

    fetched_user = await auth_repository.get_user_by_id(user.id)
    assert fetched_user is not None
    assert fetched_user.id == user.id
    assert fetched_user.email == user.email


@pytest.mark.integration
async def test_get_user_by_id_not_found_mongo(auth_repository: AuthRepositoryMongoDB):
    with pytest.raises(UserDoesNotExists) as exc_info:
        await auth_repository.get_user_by_id("64b000000000000000000000")

    assert exc_info.value.status_code == 400


# -------------------------------------------------------------
# 4. اختبارات جلب المستخدم بالبريد في MongoDB (get_user_by_email)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_get_user_by_email_success_mongo(auth_repository: AuthRepositoryMongoDB):
    email = "mongo_repo_get_by_email@test.com"
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
async def test_get_user_by_email_not_found_mongo(auth_repository: AuthRepositoryMongoDB):
    with pytest.raises(UserDoesNotExists) as exc_info:
        await auth_repository.get_user_by_email("non_existent_email_mongo@test.com")

    assert exc_info.value.status_code == 400


# -------------------------------------------------------------
# 5. اختبارات فحص وجود البريد في MongoDB (check_email_exists)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_check_email_exists_mongo(auth_repository: AuthRepositoryMongoDB):
    email = "mongo_repo_check_email@test.com"

    # قبل الإنشاء: يجب أن يرجع False
    exists_before = await auth_repository.check_email_exists(email)
    assert exists_before is False

    # بعد الإنشاء: يجب أن يرجع True
    await auth_repository.create_user(email=email, name="Check User", password="password123")
    exists_after = await auth_repository.check_email_exists(email)
    assert exists_after is True


# -------------------------------------------------------------
# 6. اختبارات حذف المستخدم في MongoDB (delete_user)
# -------------------------------------------------------------
@pytest.mark.integration
async def test_delete_user_success_mongo(auth_repository: AuthRepositoryMongoDB):
    user = await auth_repository.create_user(
        email="mongo_repo_delete_success@test.com",
        name="User To Delete",
        password="password123",
    )

    deleted = await auth_repository.delete_user(user.id)
    assert deleted is True

    # التأكد من عدم وجوده
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)


@pytest.mark.integration
async def test_delete_user_not_found_mongo(auth_repository: AuthRepositoryMongoDB):
    with pytest.raises(UserDoesNotExists) as exc_info:
        await auth_repository.delete_user("64b000000000000000000000")

    assert exc_info.value.status_code == 400
