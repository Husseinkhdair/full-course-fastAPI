import pytest
from fastapi.testclient import TestClient
from main import app
from Core.Session.session_pg import get_pg_rollback_session
from Core.di import (
    get_auth_repository,
    get_postgres_auth_repository,
    get_post_repository,
    get_postgres_post_repository,
)
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import AuthRepositoryPostgresSQl
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Post.Data.DataSources.PostRepositoryPostgresSQL import PostRepositoryPostgresSQL


from Features.Auth.Data.Models.AuthModelPostgres import AuthPostgresModel
from Core.security.Password import hash_password


@pytest.fixture
def client():
    """
    TestClient مع PostgreSQL Session داخل Transaction/Savepoint
    يتم إلغاؤها (Rollback) تلقائياً بعد كل اختبار، مع إدراج المستخدمين داخل الجلسة.
    """
    with get_pg_rollback_session() as session:
        auth_repo = AuthRepositoryPostgresSQl(db=session)
        post_repo = PostRepositoryPostgresSQL(db=session)

        # تهيئة المستخدمين للاختبار داخل الجلسة
        now_str = "2026-09-08 15:00:00"
        hashed = hash_password("password123")

        u1 = AuthPostgresModel(id="pg-pres-user-1", name="User 1", email="user1@test.com", password=hashed, role=Role.USER.value, status="active", created_at=now_str, updated_at=now_str)
        u2 = AuthPostgresModel(id="pg-pres-user-2", name="User 2", email="user2@test.com", password=hashed, role=Role.USER.value, status="active", created_at=now_str, updated_at=now_str)
        a1 = AuthPostgresModel(id="pg-pres-admin-1", name="Admin 1", email="admin1@test.com", password=hashed, role=Role.ADMIN.value, status="active", created_at=now_str, updated_at=now_str)
        a2 = AuthPostgresModel(id="pg-pres-admin-2", name="Admin 2", email="admin2@test.com", password=hashed, role=Role.ADMIN.value, status="active", created_at=now_str, updated_at=now_str)
        sa = AuthPostgresModel(id="pg-pres-super-1", name="Super 1", email="super@test.com", password=hashed, role=Role.SUPERADMIN.value, status="active", created_at=now_str, updated_at=now_str)
        session.add_all([u1, u2, a1, a2, sa])
        session.commit()

        app.dependency_overrides[get_auth_repository] = lambda: auth_repo
        app.dependency_overrides[get_postgres_auth_repository] = lambda: auth_repo
        app.dependency_overrides[get_post_repository] = lambda: post_repo
        app.dependency_overrides[get_postgres_post_repository] = lambda: post_repo

        with TestClient(app) as test_client:
            yield test_client

        app.dependency_overrides.clear()


@pytest.fixture
def user1_token():
    return generate_token(JWTPayload(id="pg-pres-user-1", email="user1@test.com", role=Role.USER.value))


@pytest.fixture
def user2_token():
    return generate_token(JWTPayload(id="pg-pres-user-2", email="user2@test.com", role=Role.USER.value))


@pytest.fixture
def admin1_token():
    return generate_token(JWTPayload(id="pg-pres-admin-1", email="admin1@test.com", role=Role.ADMIN.value))


@pytest.fixture
def admin2_token():
    return generate_token(JWTPayload(id="pg-pres-admin-2", email="admin2@test.com", role=Role.ADMIN.value))


@pytest.fixture
def superadmin_token():
    return generate_token(JWTPayload(id="pg-pres-super-1", email="super@test.com", role=Role.SUPERADMIN.value))


# ----------------------------------------------------------------------
# 1. اختبارات المصادقة (Authentication Guards)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_pg_create_post_unauthenticated(client: TestClient):
    client.cookies.clear()
    res = client.post("/post", json={"title": "No Auth", "content": "No Auth"})
    assert res.status_code == 401


@pytest.mark.integration
def test_pg_update_post_unauthenticated(client: TestClient):
    client.cookies.clear()
    res = client.put("/post/fake-id", json={"title": "No Auth", "content": "No Auth"})
    assert res.status_code == 401


@pytest.mark.integration
def test_pg_delete_post_unauthenticated(client: TestClient):
    client.cookies.clear()
    res = client.delete("/post/fake-id")
    assert res.status_code == 401


# ----------------------------------------------------------------------
# 2. إنشاء واستعراض البوستات (Create & Read)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_pg_create_and_get_post_flow(client: TestClient, user1_token: str):
    # 1. إنشاء بوست
    create_res = client.post(
        "/post",
        json={"title": "PG Pres Title", "content": "PG Pres Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert create_res.status_code == 201
    post_data = create_res.json()
    post_id = post_data["id"]
    assert post_data["title"] == "PG Pres Title"
    assert post_data["content"] == "PG Pres Content"
    assert post_data["author_id"] == "pg-pres-user-1"
    assert post_data["author_role"] == Role.USER.value

    # 2. جلب البوست بالمعرف
    get_res = client.get(f"/post/{post_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == post_id

    # 3. جلب قائمة البوستات
    list_res = client.get("/post?limit=10&offset=0")
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)


@pytest.mark.integration
def test_pg_get_post_not_found(client: TestClient):
    res = client.get("/post/non-existent-id")
    assert res.status_code == 404


# ----------------------------------------------------------------------
# 3. اختبارات صلاحيات التعديل (Update Post RBAC)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_pg_author_can_update_own_post(client: TestClient, user1_token: str):
    # إنشاء بوست
    create_res = client.post(
        "/post",
        json={"title": "Original Title", "content": "Original Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    # تعديل بواسطة المؤلف نفسه
    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Updated Title", "content": "Updated Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title"
    assert update_res.json()["content"] == "Updated Content"


@pytest.mark.integration
def test_pg_user_cannot_update_other_user_post(client: TestClient, user1_token: str, user2_token: str):
    # إنشاء بوست بواسطة User 1
    create_res = client.post(
        "/post",
        json={"title": "User 1 Post", "content": "Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    # محاولة تعديل بواسطة User 2 (يجب أن ترفض 403)
    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    assert update_res.status_code == 403


@pytest.mark.integration
def test_pg_admin_can_update_regular_user_post(client: TestClient, user1_token: str, admin1_token: str):
    # بوست مستخدم عادي
    create_res = client.post(
        "/post",
        json={"title": "User Post", "content": "User Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    # تعديل بواسطة الأدمن (مسموح)
    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Admin Modified Title"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Admin Modified Title"


@pytest.mark.integration
def test_pg_admin_cannot_update_another_admin_post(client: TestClient, admin1_token: str, admin2_token: str):
    # بوست الأدمن 1
    create_res = client.post(
        "/post",
        json={"title": "Admin 1 Post", "content": "Content"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    post_id = create_res.json()["id"]

    # محاولة تعديل بواسطة الأدمن 2 (يجب أن ترفض 403)
    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Admin 2 Edit Attempt"},
        headers={"Authorization": f"Bearer {admin2_token}"},
    )
    assert update_res.status_code == 403


@pytest.mark.integration
def test_pg_admin_cannot_update_superadmin_post(client: TestClient, superadmin_token: str, admin1_token: str):
    # بوست السوبر أدمن
    create_res = client.post(
        "/post",
        json={"title": "SuperAdmin Post", "content": "Content"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    post_id = create_res.json()["id"]

    # محاولة تعديل بواسطة الأدمن (يجب أن ترفض 403)
    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Admin Trying Edit SuperAdmin"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    assert update_res.status_code == 403


@pytest.mark.integration
def test_pg_superadmin_can_update_any_post(client: TestClient, admin1_token: str, superadmin_token: str):
    # بوست الأدمن
    create_res = client.post(
        "/post",
        json={"title": "Admin Post", "content": "Content"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    post_id = create_res.json()["id"]

    # تعديل بواسطة السوبر أدمن (مسموح)
    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "SuperAdmin Overwrite"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "SuperAdmin Overwrite"


# ----------------------------------------------------------------------
# 4. اختبارات صلاحيات الحذف (Delete Post RBAC)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_pg_author_can_delete_own_post(client: TestClient, user1_token: str):
    create_res = client.post(
        "/post",
        json={"title": "Delete Me", "content": "Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {user1_token}"})
    assert del_res.status_code == 200
    assert del_res.json() is True

    # التأكد من عدم وجوده 404
    assert client.get(f"/post/{post_id}").status_code == 404


@pytest.mark.integration
def test_pg_user_cannot_delete_other_user_post(client: TestClient, user1_token: str, user2_token: str):
    create_res = client.post(
        "/post",
        json={"title": "User 1 Delete Test", "content": "Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {user2_token}"})
    assert del_res.status_code == 403


@pytest.mark.integration
def test_pg_admin_can_delete_regular_user_post(client: TestClient, user1_token: str, admin1_token: str):
    create_res = client.post(
        "/post",
        json={"title": "User Post To Delete", "content": "Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {admin1_token}"})
    assert del_res.status_code == 200
    assert del_res.json() is True


@pytest.mark.integration
def test_pg_admin_cannot_delete_another_admin_post(client: TestClient, admin1_token: str, admin2_token: str):
    create_res = client.post(
        "/post",
        json={"title": "Admin 1 Post", "content": "Content"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {admin2_token}"})
    assert del_res.status_code == 403


@pytest.mark.integration
def test_pg_admin_cannot_delete_superadmin_post(client: TestClient, superadmin_token: str, admin1_token: str):
    create_res = client.post(
        "/post",
        json={"title": "SuperAdmin Post", "content": "Content"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {admin1_token}"})
    assert del_res.status_code == 403


@pytest.mark.integration
def test_pg_superadmin_can_delete_any_post(client: TestClient, admin1_token: str, superadmin_token: str):
    create_res = client.post(
        "/post",
        json={"title": "Admin Post For Super Delete", "content": "Content"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {superadmin_token}"})
    assert del_res.status_code == 200
    assert del_res.json() is True


# ----------------------------------------------------------------------
# 5. اختبارات الحذف المتتابع والتحقق من وجود المستخدم (Postgres)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_pg_delete_user_cascades_posts(client: TestClient, admin1_token: str, user1_token: str):
    """عند حذف مستخدم عبر /auth/user/id/{id}، تحذف بوستاته تلقائياً من PostgreSQL"""
    # 1. إنشاء بوستين بواسطة user 1
    p1_res = client.post(
        "/post",
        json={"title": "Cascade Post 1", "content": "Content 1"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    p2_res = client.post(
        "/post",
        json={"title": "Cascade Post 2", "content": "Content 2"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    p1_id = p1_res.json()["id"]
    p2_id = p2_res.json()["id"]

    # التأكد من وجودهما
    assert client.get(f"/post/{p1_id}").status_code == 200
    assert client.get(f"/post/{p2_id}").status_code == 200

    # 2. حذف المستخدم pg-pres-user-1 بواسطة الأدمن
    del_user_res = client.delete(
        "/auth/user/id/pg-pres-user-1",
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    assert del_user_res.status_code == 200

    # 3. التحقق من أن البوستين حُذفا تلقائياً (404)
    assert client.get(f"/post/{p1_id}").status_code == 404
    assert client.get(f"/post/{p2_id}").status_code == 404

    # 4. محاولة إنشاء بوست بتوكن المستخدم المحذوف تفشل بـ 400 (User does not exist)
    post_del_create = client.post(
        "/post",
        json={"title": "Post By Deleted User", "content": "Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert post_del_create.status_code == 400


@pytest.mark.integration
def test_pg_post_operations_reject_ghost_user(client: TestClient):
    """التحقق من رفض عمليات البوست لمستخدم غير موجود بالـ Database"""
    ghost_token = generate_token(JWTPayload(id="ghost-id-pg", email="ghost@test.com", role=Role.USER.value))

    res = client.post(
        "/post",
        json={"title": "Ghost Post", "content": "Ghost Content"},
        headers={"Authorization": f"Bearer {ghost_token}"},
    )
    assert res.status_code == 400

