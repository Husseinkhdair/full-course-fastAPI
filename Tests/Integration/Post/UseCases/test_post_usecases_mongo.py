import pytest
from Core.Session.sessiong_mongos import get_clean_mongo_collection
from Core.errors.AuthErrors import UserDoesNotExists
from Core.errors.PostErrors import PostNotFound, PostPermissionDenied
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB
from Features.Auth.Domain.Entities.UserEntity import Role, Status
from Features.Auth.Domain.UseCases.DeleteUserUseCase import DeleteUserUseCase
from Features.Post.Data.DataSources.PostRepositoryMongoDB import PostRepositoryMongoDB
from Features.Post.Domain.UseCases.CreatePostUseCase import CreatePostUseCase
from Features.Post.Domain.UseCases.DeletePostUseCase import DeletePostUseCase
from Features.Post.Domain.UseCases.GetPostByIdUseCase import GetPostByIdUseCase
from Features.Post.Domain.UseCases.ListPostsUseCase import ListPostsUseCase
from Features.Post.Domain.UseCases.UpdatePostUseCase import UpdatePostUseCase


@pytest.fixture
async def post_repository():
    async with get_clean_mongo_collection(collection_name="test_posts") as collection:
        yield PostRepositoryMongoDB(collection=collection)


@pytest.fixture
async def auth_repository():
    async with get_clean_mongo_collection(collection_name="test_users_posts") as collection:
        yield AuthRepositoryMongoDB(collection=collection)


@pytest.fixture
def user1_token():
    return generate_token(JWTPayload(id="mongo-user-1", email="user1@test.com", role=Role.USER.value))


@pytest.fixture
def user2_token():
    return generate_token(JWTPayload(id="mongo-user-2", email="user2@test.com", role=Role.USER.value))


@pytest.fixture
def admin1_token():
    return generate_token(JWTPayload(id="mongo-admin-1", email="admin1@test.com", role=Role.ADMIN.value))


@pytest.fixture
def admin2_token():
    return generate_token(JWTPayload(id="mongo-admin-2", email="admin2@test.com", role=Role.ADMIN.value))


@pytest.fixture
def superadmin_token():
    return generate_token(JWTPayload(id="mongo-super-1", email="super@test.com", role=Role.SUPERADMIN.value))


@pytest.mark.integration
async def test_create_post_usecase_mongo(post_repository: PostRepositoryMongoDB, user1_token: str):
    create_uc = CreatePostUseCase(post_repository)
    post = await create_uc.execute(
        title="UC Mongo Title",
        content="UC Mongo Content",
        token=user1_token,
    )

    assert post.id is not None
    assert post.title == "UC Mongo Title"
    assert post.author_id == "mongo-user-1"
    assert post.author_role == Role.USER.value


@pytest.mark.integration
async def test_get_and_list_post_usecase_mongo(post_repository: PostRepositoryMongoDB, user1_token: str):
    create_uc = CreatePostUseCase(post_repository)
    get_uc = GetPostByIdUseCase(post_repository)
    list_uc = ListPostsUseCase(post_repository)

    post = await create_uc.execute(
        title="Get Mongo Post",
        content="Get Mongo Content",
        token=user1_token,
    )

    fetched = await get_uc.execute(post.id)
    assert fetched.id == post.id

    all_posts = await list_uc.execute(limit=10, offset=0)
    assert len(all_posts) >= 1


# ----------------------------------------------------------------------
# سيناريوهات الصلاحيات والتعديل في MongoDB (UpdatePostUseCase RBAC)
# ----------------------------------------------------------------------

@pytest.mark.integration
async def test_update_post_by_author_success_mongo(
    post_repository: PostRepositoryMongoDB, user1_token: str
):
    """المؤلف يستطيع تعديل البوست الخاص به بنجاح"""
    create_uc = CreatePostUseCase(post_repository)
    update_uc = UpdatePostUseCase(post_repository)

    post = await create_uc.execute("Author Title", "Author Content", token=user1_token)

    updated = await update_uc.execute(
        post_id=post.id,
        token=user1_token,
        title="New Author Title",
        content="New Author Content",
    )
    assert updated.title == "New Author Title"
    assert updated.content == "New Author Content"


@pytest.mark.integration
async def test_user_cannot_update_other_user_post_mongo(
    post_repository: PostRepositoryMongoDB, user1_token: str, user2_token: str
):
    """مستخدم عادي لا يستطيع تعديل بوست مستخدم آخر (403)"""
    create_uc = CreatePostUseCase(post_repository)
    update_uc = UpdatePostUseCase(post_repository)

    post = await create_uc.execute("User1 Title", "Content", token=user1_token)

    with pytest.raises(PostPermissionDenied) as exc_info:
        await update_uc.execute(
            post_id=post.id,
            token=user2_token,
            title="Hacked Title",
        )
    assert exc_info.value.status_code == 403


@pytest.mark.integration
async def test_admin_can_update_regular_user_post_mongo(
    post_repository: PostRepositoryMongoDB, user1_token: str, admin1_token: str
):
    """الأدمن يستطيع تعديل بوست مستخدم عادي"""
    create_uc = CreatePostUseCase(post_repository)
    update_uc = UpdatePostUseCase(post_repository)

    post = await create_uc.execute("User Title", "User Content", token=user1_token)

    updated = await update_uc.execute(
        post_id=post.id,
        token=admin1_token,
        title="Admin Edited Title",
        content="Admin Edited Content",
    )
    assert updated.title == "Admin Edited Title"


@pytest.mark.integration
async def test_admin_cannot_update_another_admin_post_mongo(
    post_repository: PostRepositoryMongoDB, admin1_token: str, admin2_token: str
):
    """الأدمن لا يستطيع تعديل بوست أدمن آخر (403)"""
    create_uc = CreatePostUseCase(post_repository)
    update_uc = UpdatePostUseCase(post_repository)

    admin1_post = await create_uc.execute("Admin1 Title", "Admin1 Content", token=admin1_token)

    with pytest.raises(PostPermissionDenied) as exc_info:
        await update_uc.execute(
            post_id=admin1_post.id,
            token=admin2_token,
            title="Admin2 Update Attempt",
        )
    assert exc_info.value.status_code == 403


@pytest.mark.integration
async def test_admin_cannot_update_superadmin_post_mongo(
    post_repository: PostRepositoryMongoDB, superadmin_token: str, admin1_token: str
):
    """الأدمن لا يستطيع تعديل بوست سوبر أدمن (403)"""
    create_uc = CreatePostUseCase(post_repository)
    update_uc = UpdatePostUseCase(post_repository)

    super_post = await create_uc.execute("Super Title", "Super Content", token=superadmin_token)

    with pytest.raises(PostPermissionDenied) as exc_info:
        await update_uc.execute(
            post_id=super_post.id,
            token=admin1_token,
            title="Admin Trying To Edit SuperAdmin",
        )
    assert exc_info.value.status_code == 403


@pytest.mark.integration
async def test_superadmin_can_update_any_post_mongo(
    post_repository: PostRepositoryMongoDB, admin1_token: str, superadmin_token: str
):
    """السوبر أدمن يمتلك صلاحية مطلقة لتعديل أي بوست (يوزر أو أدمن)"""
    create_uc = CreatePostUseCase(post_repository)
    update_uc = UpdatePostUseCase(post_repository)

    admin_post = await create_uc.execute("Admin Title", "Admin Content", token=admin1_token)

    updated = await update_uc.execute(
        post_id=admin_post.id,
        token=superadmin_token,
        title="SuperAdmin Overwrite",
    )
    assert updated.title == "SuperAdmin Overwrite"


# ----------------------------------------------------------------------
# سيناريوهات الصلاحيات والحذف في MongoDB (DeletePostUseCase RBAC)
# ----------------------------------------------------------------------

@pytest.mark.integration
async def test_delete_post_by_author_success_mongo(
    post_repository: PostRepositoryMongoDB, user1_token: str
):
    """المؤلف يستطيع حذف البوست الخاص به"""
    create_uc = CreatePostUseCase(post_repository)
    delete_uc = DeletePostUseCase(post_repository)

    post = await create_uc.execute("Delete Title", "Content", token=user1_token)

    result = await delete_uc.execute(
        post_id=post.id,
        token=user1_token,
    )
    assert result is True


@pytest.mark.integration
async def test_user_cannot_delete_other_user_post_mongo(
    post_repository: PostRepositoryMongoDB, user1_token: str, user2_token: str
):
    """مستخدم عادي لا يستطيع حذف بوست مستخدم آخر (403)"""
    create_uc = CreatePostUseCase(post_repository)
    delete_uc = DeletePostUseCase(post_repository)

    post = await create_uc.execute("User1 Post", "Content", token=user1_token)

    with pytest.raises(PostPermissionDenied) as exc_info:
        await delete_uc.execute(
            post_id=post.id,
            token=user2_token,
        )
    assert exc_info.value.status_code == 403


@pytest.mark.integration
async def test_admin_can_delete_regular_user_post_mongo(
    post_repository: PostRepositoryMongoDB, user1_token: str, admin1_token: str
):
    """الأدمن يستطيع حذف بوست مستخدم عادي"""
    create_uc = CreatePostUseCase(post_repository)
    delete_uc = DeletePostUseCase(post_repository)

    post = await create_uc.execute("User Post", "Content", token=user1_token)

    result = await delete_uc.execute(
        post_id=post.id,
        token=admin1_token,
    )
    assert result is True


@pytest.mark.integration
async def test_admin_cannot_delete_another_admin_post_mongo(
    post_repository: PostRepositoryMongoDB, admin1_token: str, admin2_token: str
):
    """الأدمن لا يستطيع حذف بوست أدمن آخر (403)"""
    create_uc = CreatePostUseCase(post_repository)
    delete_uc = DeletePostUseCase(post_repository)

    admin1_post = await create_uc.execute("Admin1 Post", "Content", token=admin1_token)

    with pytest.raises(PostPermissionDenied) as exc_info:
        await delete_uc.execute(
            post_id=admin1_post.id,
            token=admin2_token,
        )
    assert exc_info.value.status_code == 403


@pytest.mark.integration
async def test_admin_cannot_delete_superadmin_post_mongo(
    post_repository: PostRepositoryMongoDB, superadmin_token: str, admin1_token: str
):
    """الأدمن لا يستطيع حذف بوست سوبر أدمن (403)"""
    create_uc = CreatePostUseCase(post_repository)
    delete_uc = DeletePostUseCase(post_repository)

    super_post = await create_uc.execute("Super Post", "Content", token=superadmin_token)

    with pytest.raises(PostPermissionDenied) as exc_info:
        await delete_uc.execute(
            post_id=super_post.id,
            token=admin1_token,
        )
    assert exc_info.value.status_code == 403


@pytest.mark.integration
async def test_superadmin_can_delete_any_post_mongo(
    post_repository: PostRepositoryMongoDB, admin1_token: str, superadmin_token: str
):
    """السوبر أدمن يستطيع حذف أي بوست (يوزر أو أدمن)"""
    create_uc = CreatePostUseCase(post_repository)
    delete_uc = DeletePostUseCase(post_repository)

    admin_post = await create_uc.execute("Admin Post", "Content", token=admin1_token)

    result = await delete_uc.execute(
        post_id=admin_post.id,
        token=superadmin_token,
    )
    assert result is True


# ----------------------------------------------------------------------
# سيناريوهات التحقق من وجود المستخدم والحذف المتتابع للبوستات (MongoDB)
# ----------------------------------------------------------------------

@pytest.mark.integration
async def test_post_operations_reject_nonexistent_or_deleted_user_mongo(
    post_repository: PostRepositoryMongoDB,
    auth_repository: AuthRepositoryMongoDB,
):
    """التحقق من أن أي عملية بوست ترفض إذا كان المستخدم غير موجود أو محذوفاً في MongoDB"""
    create_uc = CreatePostUseCase(post_repository=post_repository, auth_repository=auth_repository)
    update_uc = UpdatePostUseCase(post_repository=post_repository, auth_repository=auth_repository)
    delete_uc = DeletePostUseCase(post_repository=post_repository, auth_repository=auth_repository)

    # توكن لمستخدم وهمي غير موجود في DB
    ghost_token = generate_token(JWTPayload(id="64b000000000000000000001", email="ghost@test.com", role=Role.USER.value))

    # 1. محاولة إنشاء بوست بمستخدم غير موجود
    with pytest.raises(UserDoesNotExists):
        await create_uc.execute(title="Ghost Title", content="Ghost Content", token=ghost_token)

    # إنشاء مستخدم حقيقي وبوست له
    real_user = await auth_repository.create_user("real_author_mongo@test.com", "Real Author", "pwd123")
    real_token = generate_token(JWTPayload(id=real_user.id, email=real_user.email, role=Role.USER.value))
    post = await create_uc.execute(title="Real Title", content="Real Content", token=real_token)

    # 2. محاولة تعديل البوست بمستخدم غير موجود
    with pytest.raises(UserDoesNotExists):
        await update_uc.execute(post_id=post.id, token=ghost_token, title="Hacked")

    # 3. محاولة حذف البوست بمستخدم غير موجود
    with pytest.raises(UserDoesNotExists):
        await delete_uc.execute(post_id=post.id, token=ghost_token)


@pytest.mark.integration
async def test_delete_user_cascades_posts_mongo(
    post_repository: PostRepositoryMongoDB,
    auth_repository: AuthRepositoryMongoDB,
):
    """عند حذف مستخدم مهما كانت رتبته في MongoDB، تحذف جميع البوستات الخاصة به تلقائياً"""
    create_uc = CreatePostUseCase(post_repository=post_repository, auth_repository=auth_repository)
    del_user_uc = DeleteUserUseCase(auth_repository=auth_repository, post_repository=post_repository)

    # 1. إنشاء أدمن منفذ لحذف المستخدم
    admin_user = await auth_repository.create_user(
        "admin_exec_mongo@test.com", "Admin Exec", "pwd123", role=Role.ADMIN
    )
    admin_token = generate_token(JWTPayload(id=admin_user.id, email=admin_user.email, role=Role.ADMIN.value))

    # 2. إنشاء مستخدم عادي وإنشاء بوستات له
    target_user = await auth_repository.create_user(
        "author_to_delete_mongo@test.com", "Author To Delete", "pwd123", role=Role.USER
    )
    user_token = generate_token(JWTPayload(id=target_user.id, email=target_user.email, role=Role.USER.value))

    post1 = await create_uc.execute("Post 1 Mongo", "Content 1", token=user_token)
    post2 = await create_uc.execute("Post 2 Mongo", "Content 2", token=user_token)

    # التأكد من وجود البوستين في MongoDB
    assert await post_repository.get_post_by_id(post1.id) is not None
    assert await post_repository.get_post_by_id(post2.id) is not None

    # 3. حذف المستخدم بواسطة الأدمن
    deleted = await del_user_uc.execute(user_id=target_user.id, token=admin_token)
    assert deleted is True

    # 4. التأكد من أن المستخدم تم حذفه
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(target_user.id)

    # 5. التأكد من أن جميع بوستات المستخدم تم حذفها تلقائياً
    with pytest.raises(PostNotFound):
        await post_repository.get_post_by_id(post1.id)
    with pytest.raises(PostNotFound):
        await post_repository.get_post_by_id(post2.id)

    # 6. التأكد من أن محاولة إنشاء بوست بتوكن المستخدم المحذوف ترفض بـ UserDoesNotExists
    with pytest.raises(UserDoesNotExists):
        await create_uc.execute("Post After Deletion", "Content", token=user_token)

