import pytest
from Core.Session.sessiong_mongos import get_clean_mongo_collection
from Core.errors.PostErrors import PostNotFound
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Post.Data.DataSources.PostRepositoryMongoDB import PostRepositoryMongoDB
from Features.Post.Domain.Entities.PostEntity import PostEntity


@pytest.fixture
async def post_repository():
    """
    Fixture يربط مستودع البوستات بـ Collection مستقلة في MongoDB،
    ويتم تفريغها وحذف كل البيانات بعد كل اختبار تلقائياً (Rollback/Cleanup).
    """
    async with get_clean_mongo_collection(collection_name="test_posts") as collection:
        yield PostRepositoryMongoDB(collection=collection)


@pytest.mark.integration
async def test_create_post_success_mongo(post_repository: PostRepositoryMongoDB):
    post = PostEntity(
        title="MongoDB Test Title",
        content="MongoDB Test Content",
        author_id="author-mongo-123",
        author_role=Role.USER.value,
    )

    created = await post_repository.create_post(post)
    assert created is not None
    assert created.id is not None
    assert created.title == "MongoDB Test Title"
    assert created.content == "MongoDB Test Content"
    assert created.author_id == "author-mongo-123"
    assert created.author_role == Role.USER.value
    assert created.created_at is not None
    assert created.updated_at is not None


@pytest.mark.integration
async def test_get_post_by_id_mongo(post_repository: PostRepositoryMongoDB):
    post = PostEntity(
        title="Get By Id Mongo Title",
        content="Get By Id Mongo Content",
        author_id="author-mongo-456",
        author_role=Role.ADMIN.value,
    )
    created = await post_repository.create_post(post)

    fetched = await post_repository.get_post_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Get By Id Mongo Title"
    assert fetched.author_id == "author-mongo-456"


@pytest.mark.integration
async def test_get_post_by_id_not_found_mongo(post_repository: PostRepositoryMongoDB):
    with pytest.raises(PostNotFound) as exc_info:
        await post_repository.get_post_by_id("64b000000000000000000000")
    assert exc_info.value.status_code == 404


@pytest.mark.integration
async def test_update_post_success_mongo(post_repository: PostRepositoryMongoDB):
    post = PostEntity(
        title="Original Mongo Title",
        content="Original Mongo Content",
        author_id="author-mongo-789",
        author_role=Role.USER.value,
    )
    created = await post_repository.create_post(post)

    created.title = "Updated Mongo Title"
    created.content = "Updated Mongo Content"
    updated = await post_repository.update_post(created)

    assert updated.title == "Updated Mongo Title"
    assert updated.content == "Updated Mongo Content"

    # التحقق من قاعدة البيانات
    fetched = await post_repository.get_post_by_id(created.id)
    assert fetched.title == "Updated Mongo Title"
    assert fetched.content == "Updated Mongo Content"


@pytest.mark.integration
async def test_update_post_not_found_mongo(post_repository: PostRepositoryMongoDB):
    post = PostEntity(
        id="64b000000000000000000000",
        title="Dummy Title",
        content="Dummy Content",
        author_id="author-dummy",
        author_role=Role.USER.value,
    )
    with pytest.raises(PostNotFound) as exc_info:
        await post_repository.update_post(post)
    assert exc_info.value.status_code == 404


@pytest.mark.integration
async def test_delete_post_success_mongo(post_repository: PostRepositoryMongoDB):
    post = PostEntity(
        title="To Be Deleted Mongo",
        content="Content To Be Deleted Mongo",
        author_id="author-mongo-del",
        author_role=Role.USER.value,
    )
    created = await post_repository.create_post(post)

    result = await post_repository.delete_post(created.id)
    assert result is True

    # التأكد من عدم وجوده
    with pytest.raises(PostNotFound):
        await post_repository.get_post_by_id(created.id)


@pytest.mark.integration
async def test_delete_post_not_found_mongo(post_repository: PostRepositoryMongoDB):
    with pytest.raises(PostNotFound) as exc_info:
        await post_repository.delete_post("64b000000000000000000000")
    assert exc_info.value.status_code == 404


@pytest.mark.integration
async def test_list_posts_mongo(post_repository: PostRepositoryMongoDB):
    for i in range(3):
        post = PostEntity(
            title=f"Mongo List Post {i}",
            content=f"Content {i}",
            author_id=f"author-{i}",
            author_role=Role.USER.value,
        )
        await post_repository.create_post(post)

    posts = await post_repository.list_posts(limit=10, offset=0)
    assert len(posts) >= 3


@pytest.mark.integration
async def test_delete_posts_by_author_id_mongo(post_repository: PostRepositoryMongoDB):
    author_id = "author-mongo-bulk-del"
    for i in range(3):
        post = PostEntity(
            title=f"Mongo Author Post {i}",
            content=f"Content {i}",
            author_id=author_id,
            author_role=Role.USER.value,
        )
        await post_repository.create_post(post)

    # حذف جميع بوستات الكاتب في MongoDB
    deleted_count = await post_repository.delete_posts_by_author_id(author_id)
    assert deleted_count >= 3

    # التحقق من أن الحذف المتتابع أزال جميع بوستات هذا الكاتب
    remaining_posts = await post_repository.list_posts(limit=100, offset=0)
    author_posts = [p for p in remaining_posts if p.author_id == author_id]
    assert len(author_posts) == 0
