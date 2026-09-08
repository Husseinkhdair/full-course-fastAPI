import pytest
from fastapi.testclient import TestClient
from main import app
from Core.di import (
    get_auth_repository,
    get_mongodb_auth_repository,
    get_postgres_auth_repository,
)
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import (
    AuthRepositoryMongoDB,
)
from Features.Auth.Domain.Entities.UserEntity import Role


@pytest.fixture
def client():
    """
    TestClient مع MongoDB DataSource عبر dependency_overrides.
    """
    repo = AuthRepositoryMongoDB()
    app.dependency_overrides[get_auth_repository] = lambda: repo
    app.dependency_overrides[get_postgres_auth_repository] = lambda: repo
    app.dependency_overrides[get_mongodb_auth_repository] = lambda: repo

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_token():
    return generate_token(
        JWTPayload(id="mongo-admin-id", email="admin@test.com", role=Role.ADMIN.value)
    )


@pytest.fixture
def user_token():
    return generate_token(
        JWTPayload(id="mongo-user-id", email="user@test.com", role=Role.USER.value)
    )


# -------------------------------------------------------------
# 1. التدفق الكامل لرحلة المستخدم على MongoDB
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_full_auth_lifecycle_flow(client: TestClient, admin_token: str):
    email = "mongo_pres_lifecycle@test.com"
    name = "Mongo Lifecycle User"
    password = "password123"

    # 1. تسجيل مستخدم جديد
    reg_res = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["email"] == email
    assert reg_data["name"] == name
    assert "user_id" in reg_data
    assert reg_data["token"] is not None

    user_id = str(reg_data["user_id"])

    try:
        # 2. تسجيل الدخول
        login_res = client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert login_data["user_id"] == user_id
        assert login_data["token"] is not None

        # 3. جلب المستخدم بواسطة ID مع توكن Admin
        auth_headers = {"Authorization": f"Bearer {admin_token}"}
        get_id_res = client.get(f"/auth/user/id/{user_id}", headers=auth_headers)
        assert get_id_res.status_code == 200
        assert get_id_res.json()["user_id"] == user_id

        # 4. جلب المستخدم بواسطة Email مع توكن Admin
        get_email_res = client.get(f"/auth/user/email/{email}", headers=auth_headers)
        assert get_email_res.status_code == 200
        assert get_email_res.json()["email"] == email

        # 5. حذف المستخدم مع توكن Admin
        del_res = client.delete(f"/auth/user/id/{user_id}", headers=auth_headers)
        assert del_res.status_code == 200
        assert del_res.json() is True

        # 6. التأكد من فشل تسجيل الدخول بعد الحذف
        post_del_login = client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        assert post_del_login.status_code == 401

    finally:
        # ضمان تنظيف الحساب حتى لو فشل اختبار داخلي
        client.delete(f"/auth/user/id/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})


# -------------------------------------------------------------
# 2. فحص محاولة تسجيل إيميل مكرر في MongoDB
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_register_duplicate_email_fails(client: TestClient, admin_token: str):
    email = "mongo_pres_dup@test.com"
    data = {"name": "Duplicate Mongo", "email": email, "password": "password123"}

    res1 = client.post("/auth/register", json=data)
    assert res1.status_code == 201
    user_id = res1.json()["user_id"]

    try:
        # المحاولة الثانية يجب أن تفشل مع 400
        res2 = client.post("/auth/register", json=data)
        assert res2.status_code == 400
        assert "exists" in res2.json().get("detail", "").lower()
    finally:
        client.delete(f"/auth/user/id/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})


# -------------------------------------------------------------
# 3. تسجيل مستخدم بصلاحيات المشرف على MongoDB
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_register_admin_with_admin_token(client: TestClient, admin_token: str):
    email = "mongo_pres_new_admin@test.com"
    data = {"name": "New Mongo Admin", "email": email, "password": "password123", "role": "admin"}

    res = client.post(
        "/auth/register",
        json=data,
        headers={"access_token": admin_token},
    )
    assert res.status_code == 201
    assert res.json()["email"] == email
    assert res.json()["role"] == "admin"
    user_id = res.json()["user_id"]

    # تنظيف بواسطة superadmin لأن admin لا يمكنه حذف admin
    superadmin_token = generate_token(
        JWTPayload(id="mongo-super-id", email="super@test.com", role=Role.SUPERADMIN.value)
    )
    client.delete(f"/auth/user/id/{user_id}", headers={"Authorization": f"Bearer {superadmin_token}"})


# -------------------------------------------------------------
# 4. أخطاء تسجيل الدخول في MongoDB
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_login_wrong_password_fails(client: TestClient, admin_token: str):
    email = "mongo_pres_wrong_pwd@test.com"
    reg = client.post(
        "/auth/register",
        json={"name": "User", "email": email, "password": "password123"},
    )
    user_id = reg.json()["user_id"]

    try:
        # كلمة سر خاطئة
        res = client.post(
            "/auth/login",
            json={"email": email, "password": "wrongpassword999"},
        )
        assert res.status_code == 401
    finally:
        client.delete(f"/auth/user/id/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})


@pytest.mark.integration
def test_mongo_login_unregistered_email_fails(client: TestClient):
    res = client.post(
        "/auth/login",
        json={"email": "mongo_unregistered_123@test.com", "password": "password123"},
    )
    assert res.status_code == 401


# -------------------------------------------------------------
# 5. منع المستخدم العادي من المسارات المحمية في MongoDB (403)
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_protected_routes_forbidden_for_normal_user(
    client: TestClient, user_token: str, admin_token: str
):
    reg_res = client.post(
        "/auth/register",
        json={"name": "Target", "email": "mongo_guard_user@test.com", "password": "password123"},
    )
    user_id = reg_res.json()["user_id"]
    email = "mongo_guard_user@test.com"

    auth_headers = {"Authorization": f"Bearer {user_token}"}

    try:
        # 1. منع get by id
        res1 = client.get(f"/auth/user/id/{user_id}", headers=auth_headers)
        assert res1.status_code == 403

        # 2. منع get by email
        res2 = client.get(f"/auth/user/email/{email}", headers=auth_headers)
        assert res2.status_code == 403

        # 3. منع delete
        res3 = client.delete(f"/auth/user/id/{user_id}", headers=auth_headers)
        assert res3.status_code == 403
    finally:
        client.delete(f"/auth/user/id/{user_id}", headers={"Authorization": f"Bearer {admin_token}"})


# -------------------------------------------------------------
# 6. فحص التوكن المفقود أو غير الصالح (401 Unauthorized)
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_protected_routes_without_token_fail(client: TestClient):
    res = client.get("/auth/user/id/some-mongo-id")
    assert res.status_code == 401


@pytest.mark.integration
def test_mongo_protected_routes_with_invalid_token_fail(client: TestClient):
    auth_headers = {"Authorization": "Bearer invalid.jwt.token"}
    res = client.get("/auth/user/id/some-mongo-id", headers=auth_headers)
    assert res.status_code == 401


# -------------------------------------------------------------
# 7. البحث عن عناصر غير موجودة في MongoDB (400 Not Found)
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_admin_not_found_cases(client: TestClient, admin_token: str):
    auth_headers = {"Authorization": f"Bearer {admin_token}"}

    # get by id غير موجود
    res1 = client.get("/auth/user/id/64b000000000000000000000", headers=auth_headers)
    assert res1.status_code == 400

    # get by email غير موجود
    res2 = client.get("/auth/user/email/non_existent_mongo@test.com", headers=auth_headers)
    assert res2.status_code == 400

    # delete غير موجود
    res3 = client.delete("/auth/user/id/64b000000000000000000000", headers=auth_headers)
    assert res3.status_code == 400


# -------------------------------------------------------------
# 8. التحقق من صحة المدخلات في الـ Request Body (422)
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_input_validation_errors(client: TestClient):
    # صيغة إيميل غير صالحة
    res1 = client.post(
        "/auth/register",
        json={"name": "User", "email": "invalid-email-format", "password": "password123"},
    )
    assert res1.status_code == 422

    # كلمة سر قصيرة
    res2 = client.post(
        "/auth/register",
        json={"name": "User", "email": "valid@test.com", "password": "123"},
    )
    assert res2.status_code == 422


# -------------------------------------------------------------
# 9. منع الأدمن من حذف أدمن آخر في MongoDB (403 Forbidden)
# -------------------------------------------------------------
@pytest.mark.integration
def test_mongo_admin_cannot_delete_another_admin(client: TestClient, admin_token: str):
    # 1. إنشاء توكن سوبر أدمن
    superadmin_token = generate_token(
        JWTPayload(id="mongo-super-id", email="super@test.com", role=Role.SUPERADMIN.value)
    )

    # 2. إنشاء مشرف جديد (Admin) بتمرير توكن السوبر أدمن مع تحديد role=admin
    reg_res = client.post(
        "/auth/register",
        json={
            "name": "Target Mongo Admin",
            "email": "mongo_target_admin_pres@test.com",
            "password": "password123",
            "role": "admin",
        },
        headers={"access_token": superadmin_token},
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["role"] == "admin"
    target_admin_id = str(reg_res.json()["user_id"])

    try:
        # 3. محاولة المشرف (Admin) حذف المشرف المستهدف -> يجب أن تُرفض بكود 403
        del_res = client.delete(
            f"/auth/user/id/{target_admin_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert del_res.status_code == 403
        assert "admin cannot delete" in del_res.json().get("detail", "").lower()

        # 4. السوبر أدمن يملك الصلاحية لحذف المشرف -> يجب أن تنجح
        super_del_res = client.delete(
            f"/auth/user/id/{target_admin_id}",
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )
        assert super_del_res.status_code == 200
        assert super_del_res.json() is True
    finally:
        # تنظيف احتياطي
        client.delete(f"/auth/user/id/{target_admin_id}", headers={"Authorization": f"Bearer {superadmin_token}"})

