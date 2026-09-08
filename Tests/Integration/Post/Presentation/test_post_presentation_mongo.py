import asyncio
import pytest
from fastapi.testclient import TestClient
from main import app
from Core.DataBase.MongoDb import get_db
from Core.di import (
    get_auth_repository,
    get_mongodb_auth_repository,
    get_postgres_auth_repository,
    get_post_repository,
    get_postgres_post_repository,
    get_mongodb_post_repository,
)
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Post.Data.DataSources.PostRepositoryMongoDB import PostRepositoryMongoDB


from pymongo import MongoClient
from Core.Settings import SettingsApp
from Core.security.Password import hash_password

settings = SettingsApp()


@pytest.fixture
def client():
    """
    TestClient موصول بـ MongoDB مع تهيئة المستخدمين وتنظيف البيانات (Rollback/Cleanup)
    تلقائياً بعد كل اختبار باستخدام Collections معزولة للاختبارات.
    """
    sync_client = MongoClient(settings.mongodb_url)
    sync_db = sync_client[settings.mongodb_name]
    sync_user_coll = sync_db["test_users_pres"]
    sync_post_coll = sync_db["test_posts_pres"]

    # تنظيف مسبق
    sync_user_coll.delete_many({})
    sync_post_coll.delete_many({})

    # تهيئة المستخدمين للاختبار
    now_str = "2026-09-08 15:00:00"
    hashed = hash_password("password123")

    sync_user_coll.insert_many([
        {"id": "mongo-pres-user-1", "_id": "mongo-pres-user-1", "name": "User 1", "email": "user1@test.com", "password": hashed, "role": Role.USER.value, "status": "active", "created_at": now_str, "updated_at": now_str},
        {"id": "mongo-pres-user-2", "_id": "mongo-pres-user-2", "name": "User 2", "email": "user2@test.com", "password": hashed, "role": Role.USER.value, "status": "active", "created_at": now_str, "updated_at": now_str},
        {"id": "mongo-pres-admin-1", "_id": "mongo-pres-admin-1", "name": "Admin 1", "email": "admin1@test.com", "password": hashed, "role": Role.ADMIN.value, "status": "active", "created_at": now_str, "updated_at": now_str},
        {"id": "mongo-pres-admin-2", "_id": "mongo-pres-admin-2", "name": "Admin 2", "email": "admin2@test.com", "password": hashed, "role": Role.ADMIN.value, "status": "active", "created_at": now_str, "updated_at": now_str},
        {"id": "mongo-pres-super-1", "_id": "mongo-pres-super-1", "name": "Super 1", "email": "super@test.com", "password": hashed, "role": Role.SUPERADMIN.value, "status": "active", "created_at": now_str, "updated_at": now_str},
    ])

    from Core.DataBase.MongoDb import CollectionProxy
    auth_coll_proxy = CollectionProxy(lambda: "test_users_pres")
    post_coll_proxy = CollectionProxy(lambda: "test_posts_pres")

    auth_repo = AuthRepositoryMongoDB(collection=auth_coll_proxy)
    post_repo = PostRepositoryMongoDB(collection=post_coll_proxy)

    app.dependency_overrides[get_auth_repository] = lambda: auth_repo
    app.dependency_overrides[get_postgres_auth_repository] = lambda: auth_repo
    app.dependency_overrides[get_mongodb_auth_repository] = lambda: auth_repo
    app.dependency_overrides[get_post_repository] = lambda: post_repo
    app.dependency_overrides[get_postgres_post_repository] = lambda: post_repo
    app.dependency_overrides[get_mongodb_post_repository] = lambda: post_repo

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    sync_user_coll.delete_many({})
    sync_post_coll.delete_many({})
    sync_client.close()


@pytest.fixture
def user1_token():
    return generate_token(JWTPayload(id="mongo-pres-user-1", email="user1@test.com", role=Role.USER.value))


@pytest.fixture
def user2_token():
    return generate_token(JWTPayload(id="mongo-pres-user-2", email="user2@test.com", role=Role.USER.value))


@pytest.fixture
def admin1_token():
    return generate_token(JWTPayload(id="mongo-pres-admin-1", email="admin1@test.com", role=Role.ADMIN.value))


@pytest.fixture
def admin2_token():
    return generate_token(JWTPayload(id="mongo-pres-admin-2", email="admin2@test.com", role=Role.ADMIN.value))


@pytest.fixture
def superadmin_token():
    return generate_token(JWTPayload(id="mongo-pres-super-1", email="super@test.com", role=Role.SUPERADMIN.value))


# ----------------------------------------------------------------------
# 1. اختبارات المصادقة في MongoDB (Authentication Guards)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_mongo_create_post_unauthenticated(client: TestClient):
    client.cookies.clear()
    res = client.post("/post", json={"title": "No Auth", "content": "No Auth"})
    assert res.status_code == 401


@pytest.mark.integration
def test_mongo_update_post_unauthenticated(client: TestClient):
    client.cookies.clear()
    res = client.put("/post/64b000000000000000000000", json={"title": "No Auth", "content": "No Auth"})
    assert res.status_code == 401


@pytest.mark.integration
def test_mongo_delete_post_unauthenticated(client: TestClient):
    client.cookies.clear()
    res = client.delete("/post/64b000000000000000000000")
    assert res.status_code == 401


# ----------------------------------------------------------------------
# 2. إنشاء واستعراض البوستات في MongoDB (Create & Read)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_mongo_create_and_get_post_flow(client: TestClient, user1_token: str):
    # 1. إنشاء بوست
    create_res = client.post(
        "/post",
        json={"title": "Mongo Pres Title", "content": "Mongo Pres Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert create_res.status_code == 201
    post_data = create_res.json()
    post_id = post_data["id"]
    assert post_data["title"] == "Mongo Pres Title"
    assert post_data["content"] == "Mongo Pres Content"
    assert post_data["author_id"] == "mongo-pres-user-1"
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
def test_mongo_get_post_not_found(client: TestClient):
    res = client.get("/post/64b000000000000000000000")
    assert res.status_code == 404


# ----------------------------------------------------------------------
# 3. اختبارات صلاحيات التعديل في MongoDB (Update Post RBAC)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_mongo_author_can_update_own_post(client: TestClient, user1_token: str):
    create_res = client.post(
        "/post",
        json={"title": "Original Mongo Title", "content": "Original Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Updated Mongo Title", "content": "Updated Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Mongo Title"
    assert update_res.json()["content"] == "Updated Content"


@pytest.mark.integration
def test_mongo_user_cannot_update_other_user_post(client: TestClient, user1_token: str, user2_token: str):
    create_res = client.post(
        "/post",
        json={"title": "User 1 Post", "content": "Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    assert update_res.status_code == 403


@pytest.mark.integration
def test_mongo_admin_can_update_regular_user_post(client: TestClient, user1_token: str, admin1_token: str):
    create_res = client.post(
        "/post",
        json={"title": "User Post", "content": "User Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Admin Modified Title"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Admin Modified Title"


@pytest.mark.integration
def test_mongo_admin_cannot_update_another_admin_post(client: TestClient, admin1_token: str, admin2_token: str):
    create_res = client.post(
        "/post",
        json={"title": "Admin 1 Post", "content": "Content"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    post_id = create_res.json()["id"]

    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Admin 2 Edit Attempt"},
        headers={"Authorization": f"Bearer {admin2_token}"},
    )
    assert update_res.status_code == 403


@pytest.mark.integration
def test_mongo_admin_cannot_update_superadmin_post(client: TestClient, superadmin_token: str, admin1_token: str):
    create_res = client.post(
        "/post",
        json={"title": "SuperAdmin Post", "content": "Content"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    post_id = create_res.json()["id"]

    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "Admin Trying Edit SuperAdmin"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    assert update_res.status_code == 403


@pytest.mark.integration
def test_mongo_superadmin_can_update_any_post(client: TestClient, admin1_token: str, superadmin_token: str):
    create_res = client.post(
        "/post",
        json={"title": "Admin Post", "content": "Content"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    post_id = create_res.json()["id"]

    update_res = client.put(
        f"/post/{post_id}",
        json={"title": "SuperAdmin Overwrite"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "SuperAdmin Overwrite"


# ----------------------------------------------------------------------
# 4. اختبارات صلاحيات الحذف في MongoDB (Delete Post RBAC)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_mongo_author_can_delete_own_post(client: TestClient, user1_token: str):
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
def test_mongo_user_cannot_delete_other_user_post(client: TestClient, user1_token: str, user2_token: str):
    create_res = client.post(
        "/post",
        json={"title": "User 1 Delete Test", "content": "Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {user2_token}"})
    assert del_res.status_code == 403


@pytest.mark.integration
def test_mongo_admin_can_delete_regular_user_post(client: TestClient, user1_token: str, admin1_token: str):
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
def test_mongo_admin_cannot_delete_another_admin_post(client: TestClient, admin1_token: str, admin2_token: str):
    create_res = client.post(
        "/post",
        json={"title": "Admin 1 Post", "content": "Content"},
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {admin2_token}"})
    assert del_res.status_code == 403


@pytest.mark.integration
def test_mongo_admin_cannot_delete_superadmin_post(client: TestClient, superadmin_token: str, admin1_token: str):
    create_res = client.post(
        "/post",
        json={"title": "SuperAdmin Post", "content": "Content"},
        headers={"Authorization": f"Bearer {superadmin_token}"},
    )
    post_id = create_res.json()["id"]

    del_res = client.delete(f"/post/{post_id}", headers={"Authorization": f"Bearer {admin1_token}"})
    assert del_res.status_code == 403


@pytest.mark.integration
def test_mongo_superadmin_can_delete_any_post(client: TestClient, admin1_token: str, superadmin_token: str):
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
# 5. اختبارات الحذف المتتابع والتحقق من وجود المستخدم (MongoDB)
# ----------------------------------------------------------------------

@pytest.mark.integration
def test_mongo_delete_user_cascades_posts(client: TestClient, admin1_token: str, user1_token: str):
    """عند حذف مستخدم عبر /auth/user/id/{id}، تحذف بوستاته تلقائياً من MongoDB"""
    # 1. إنشاء بوستين بواسطة user 1
    p1_res = client.post(
        "/post",
        json={"title": "Cascade Mongo Post 1", "content": "Content 1"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    p2_res = client.post(
        "/post",
        json={"title": "Cascade Mongo Post 2", "content": "Content 2"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    p1_id = p1_res.json()["id"]
    p2_id = p2_res.json()["id"]

    # التأكد من وجودهما في MongoDB
    assert client.get(f"/post/{p1_id}").status_code == 200
    assert client.get(f"/post/{p2_id}").status_code == 200

    # 2. حذف المستخدم mongo-pres-user-1 بواسطة الأدمن
    del_user_res = client.delete(
        "/auth/user/id/mongo-pres-user-1",
        headers={"Authorization": f"Bearer {admin1_token}"},
    )
    assert del_user_res.status_code == 200

    # 3. التحقق من أن البوستين حُذفا تلقائياً (404)
    assert client.get(f"/post/{p1_id}").status_code == 404
    assert client.get(f"/post/{p2_id}").status_code == 404

    # 4. محاولة إنشاء بوست بتوكن المستخدم المحذوف تفشل بـ 400 (User does not exist)
    post_del_create = client.post(
        "/post",
        json={"title": "Post By Deleted Mongo User", "content": "Content"},
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    assert post_del_create.status_code == 400


@pytest.mark.integration
def test_mongo_post_operations_reject_ghost_user(client: TestClient):
    """التحقق من رفض عمليات البوست لمستخدم غير موجود بالـ MongoDB"""
    ghost_token = generate_token(JWTPayload(id="64b000000000000000000099", email="ghost@test.com", role=Role.USER.value))

    res = client.post(
        "/post",
        json={"title": "Ghost Mongo Post", "content": "Ghost Content"},
        headers={"Authorization": f"Bearer {ghost_token}"},
    )
    assert res.status_code == 400

