import pytest
from fastapi.testclient import TestClient
from main import app
from Core.di import (
    get_auth_repository,
    get_mongodb_auth_repository,
    get_postgres_auth_repository,
)
from Core.security.Jwt import JWTPayload, generate_token, verify_token
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import (
    AuthRepositoryMongoDB,
)
from Features.Auth.Domain.Entities.UserEntity import Role


@pytest.fixture
def mongo_client():
    """
    E2E Client مع MongoDB DataSource،
    يتم توجيه جميع عمليات المستودع إلى MongoDB وتنظيف البيانات بعد كل اختبار.
    """
    repo = AuthRepositoryMongoDB()
    app.dependency_overrides[get_auth_repository] = lambda: repo
    app.dependency_overrides[get_postgres_auth_repository] = lambda: repo
    app.dependency_overrides[get_mongodb_auth_repository] = lambda: repo

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_token():
    return generate_token(
        JWTPayload(id="mongo-e2e-admin", email="admin_mongo_e2e@test.com", role=Role.ADMIN.value)
    )


@pytest.fixture
def superadmin_token():
    return generate_token(
        JWTPayload(id="mongo-e2e-superadmin", email="super_mongo_e2e@test.com", role=Role.SUPERADMIN.value)
    )


# =====================================================================
# 1. دورة حياة المستخدم الكاملة في MongoDB (Complete User Lifecycle Journey)
# =====================================================================
@pytest.mark.e2e
def test_mongo_e2e_complete_user_lifecycle(
    mongo_client: TestClient, admin_token: str, superadmin_token: str
):
    email = "mongo_e2e_lifecycle@example.com"
    name = "Mongo E2E User"
    password = "password123"

    # الخطوة 1: تسجيل مستخدم جديد
    reg_res = mongo_client.post(
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
    register_token = reg_data["token"]

    try:
        # الخطوة 2: التحقق المشفر من توكن التسجيل (JWT Token Verification)
        reg_payload = verify_token(register_token)
        assert reg_payload is not None
        assert reg_payload.id == user_id
        assert reg_payload.email == email

        # الخطوة 3: تسجيل الدخول
        login_res = mongo_client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        assert login_res.status_code == 200
        login_data = login_res.json()
        assert login_data["user_id"] == user_id
        assert login_data["token"] is not None

        # الخطوة 4: التحقق من توكن الدخول
        login_payload = verify_token(login_data["token"])
        assert login_payload is not None
        assert login_payload.id == user_id

        # الخطوة 5: جلب بيانات المستخدم بالـ ID بواسطة المشرف
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        get_id_res = mongo_client.get(f"/auth/user/id/{user_id}", headers=admin_headers)
        assert get_id_res.status_code == 200
        assert get_id_res.json()["user_id"] == user_id
        assert get_id_res.json()["email"] == email

        # الخطوة 6: جلب بيانات المستخدم بالإيميل بواسطة المشرف
        get_email_res = mongo_client.get(f"/auth/user/email/{email}", headers=admin_headers)
        assert get_email_res.status_code == 200
        assert get_email_res.json()["email"] == email

        # الخطوة 7: حذف الحساب بواسطة المشرف
        del_res = mongo_client.delete(f"/auth/user/id/{user_id}", headers=admin_headers)
        assert del_res.status_code == 200
        assert del_res.json() is True

        # الخطوة 8: التأكد من فشل تسجيل الدخول بعد الحذف
        post_del_login = mongo_client.post(
            "/auth/login",
            json={"email": email, "password": password},
        )
        assert post_del_login.status_code == 401

        # الخطوة 9: التأكد من فشل استعلام المستخدم بعد الحذف
        post_del_get = mongo_client.get(f"/auth/user/id/{user_id}", headers=admin_headers)
        assert post_del_get.status_code == 400

    finally:
        # تنظيف الحساب احتياطياً لضمان عدم بقاء أي بيانات
        mongo_client.delete(
            f"/auth/user/id/{user_id}",
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )


# =====================================================================
# 2. عزل بيانات المستخدمين في MongoDB (Multiple Users Isolation)
# =====================================================================
@pytest.mark.e2e
def test_mongo_e2e_multiple_users_isolation(
    mongo_client: TestClient, admin_token: str, superadmin_token: str
):
    user1_email = "mongo_e2e_user1@example.com"
    user2_email = "mongo_e2e_user2@example.com"
    pwd = "password123"

    res1 = mongo_client.post("/auth/register", json={"name": "Mongo User 1", "email": user1_email, "password": pwd})
    res2 = mongo_client.post("/auth/register", json={"name": "Mongo User 2", "email": user2_email, "password": pwd})
    assert res1.status_code == 201
    assert res2.status_code == 201

    u1_id = str(res1.json()["user_id"])
    u2_id = str(res2.json()["user_id"])
    assert u1_id != u2_id

    try:
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        p1 = mongo_client.get(f"/auth/user/id/{u1_id}", headers=admin_headers).json()
        p2 = mongo_client.get(f"/auth/user/id/{u2_id}", headers=admin_headers).json()

        assert p1["email"] == user1_email
        assert p2["email"] == user2_email
    finally:
        super_headers = {"Authorization": f"Bearer {superadmin_token}"}
        mongo_client.delete(f"/auth/user/id/{u1_id}", headers=super_headers)
        mongo_client.delete(f"/auth/user/id/{u2_id}", headers=super_headers)


# =====================================================================
# 3. منع الأدمن من حذف أدمن آخر وسماح السوبر أدمن بالحذف
# =====================================================================
@pytest.mark.e2e
def test_mongo_e2e_admin_cannot_delete_another_admin(
    mongo_client: TestClient, admin_token: str, superadmin_token: str
):
    # إنشاء أدمن بواسطة السوبر أدمن
    reg_res = mongo_client.post(
        "/auth/register",
        json={
            "name": "Target Admin Mongo",
            "email": "mongo_e2e_target_admin@test.com",
            "password": "password123",
            "role": "admin",
        },
        headers={"access_token": superadmin_token},
    )
    assert reg_res.status_code == 201
    assert reg_res.json()["role"] == "admin"
    target_admin_id = str(reg_res.json()["user_id"])

    try:
        # محاولة أدمن حذف أدمن آخر يجب أن تُرفض بكود 403
        del_by_admin = mongo_client.delete(
            f"/auth/user/id/{target_admin_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert del_by_admin.status_code == 403
        assert "admin cannot delete" in del_by_admin.json().get("detail", "").lower()

        # السوبر أدمن يملك صلاحية حذف الأدمن بنجاح
        del_by_super = mongo_client.delete(
            f"/auth/user/id/{target_admin_id}",
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )
        assert del_by_super.status_code == 200
        assert del_by_super.json() is True
    finally:
        mongo_client.delete(
            f"/auth/user/id/{target_admin_id}",
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )


# =====================================================================
# 4. فحص جدران الحماية والصلاحيات في MongoDB (RBAC & Auth Guards)
# =====================================================================
@pytest.mark.e2e
def test_mongo_e2e_rbac_and_auth_guards(mongo_client: TestClient, superadmin_token: str):
    reg_res = mongo_client.post(
        "/auth/register",
        json={"name": "Guard User", "email": "mongo_guard_e2e@test.com", "password": "password123"},
    )
    user_id = str(reg_res.json()["user_id"])
    user_token = reg_res.json()["token"]

    try:
        user_headers = {"Authorization": f"Bearer {user_token}"}

        # المستخدم العادي ممنوع من الاستعلام أو الحذف (403)
        assert mongo_client.get(f"/auth/user/id/{user_id}", headers=user_headers).status_code == 403
        assert mongo_client.get("/auth/user/email/mongo_guard_e2e@test.com", headers=user_headers).status_code == 403
        assert mongo_client.delete(f"/auth/user/id/{user_id}", headers=user_headers).status_code == 403

        # طلب بدون توكن (401)
        assert mongo_client.get(f"/auth/user/id/{user_id}").status_code == 401

        # طلب بتوكن غير صالح (401)
        assert mongo_client.get(
            f"/auth/user/id/{user_id}",
            headers={"Authorization": "Bearer invalid.token.payload"},
        ).status_code == 401
    finally:
        mongo_client.delete(
            f"/auth/user/id/{user_id}",
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )


# =====================================================================
# 5. أخطاء التسجيل وتسجيل الدخول في MongoDB
# =====================================================================
@pytest.mark.e2e
def test_mongo_e2e_duplicate_email_and_login_failures(
    mongo_client: TestClient, superadmin_token: str
):
    email = "mongo_dup_login_e2e@test.com"
    pwd = "password123"

    reg_res = mongo_client.post("/auth/register", json={"name": "User", "email": email, "password": pwd})
    assert reg_res.status_code == 201
    user_id = str(reg_res.json()["user_id"])

    try:
        # تكرار التسجيل يرجع 400
        assert mongo_client.post("/auth/register", json={"name": "User", "email": email, "password": pwd}).status_code == 400

        # تسجيل دخول بكلمة مرور خاطئة (401)
        assert mongo_client.post("/auth/login", json={"email": email, "password": "wrongpassword"}).status_code == 401

        # تسجيل دخول لإيميل غير مسجل (401)
        assert mongo_client.post("/auth/login", json={"email": "nonexistent_mongo@test.com", "password": pwd}).status_code == 401
    finally:
        mongo_client.delete(
            f"/auth/user/id/{user_id}",
            headers={"Authorization": f"Bearer {superadmin_token}"},
        )


# =====================================================================
# 6. التحقق من صحة المدخلات في MongoDB (Schema Validation 422)
# =====================================================================
@pytest.mark.e2e
def test_mongo_e2e_input_validation_errors(mongo_client: TestClient):
    # بريد غير صالح
    assert mongo_client.post(
        "/auth/register",
        json={"name": "Bad", "email": "not-valid-email", "password": "password123"},
    ).status_code == 422

    # كلمة سر أقل من 6 أحرف
    assert mongo_client.post(
        "/auth/register",
        json={"name": "Bad", "email": "valid@test.com", "password": "123"},
    ).status_code == 422
