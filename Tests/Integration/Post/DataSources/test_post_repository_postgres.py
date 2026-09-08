import pytest
from sqlalchemy.orm import Session
from Core.Session.session_pg import db_session
from Core.errors.PostErrors import PostNotFound
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Post.Data.DataSources.PostRepositoryPostgresSQL import PostRepositoryPostgresSQL
from Features.Post.Domain.Entities.PostEntity import PostEntity


@pytest.fixture
def post_repository(db_session: Session) -> PostRepositoryPostgresSQL:
    """
    Fixture يربط مستودع البوستات بجلسة SQLAlchemy مع Rollback تلقائي
    بعد كل اختبار لضمان عدم ترك أي بيانات في PostgreSQL.
    """
    return PostRepositoryPostgresSQL(db=db_session)


@pytest.mark.integration
async def test_create_post_success_postgres(post_repository: PostRepositoryPostgresSQL):
    post = PostEntity(
        title="PostgreSQL Test Title",
        content="PostgreSQL Test Content",
        author_id="author-pg-123",
        author_role=Role.USER.value,
    )

    created = await post_repository.create_post(post)
    assert created is not None
    assert created.id is not None
    assert created.title == "PostgreSQL Test Title"
    assert created.content == "PostgreSQL Test Content"
    assert created.author_id == "author-pg-123"
    assert created.author_role == Role.USER.value
    assert created.created_at is not None
    assert created.updated_at is not None


@pytest.mark.integration
async def test_get_post_by_id_postgres(post_repository: PostRepositoryPostgresSQL):
    post = PostEntity(
        title="Get By Id Title",
        content="Get By Id Content",
        author_id="author-pg-456",
        author_role=Role.ADMIN.value,
    )
    created = await post_repository.create_post(post)

    fetched = await post_repository.get_post_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.title == "Get By Id Title"
    assert fetched.author_id == "author-pg-456"


@pytest.mark.integration
async def test_get_post_by_id_not_found_postgres(post_repository: PostRepositoryPostgresSQL):
    with pytest.raises(PostNotFound) as exc_info:
        await post_repository.get_post_by_id("non-existent-pg-post-id")
    assert exc_info.value.status_code == 404


@pytest.mark.integration
async def test_update_post_success_postgres(post_repository: PostRepositoryPostgresSQL):
    post = PostEntity(
        title="Original Title",
        content="Original Content",
        author_id="author-pg-789",
        author_role=Role.USER.value,
    )
    created = await post_repository.create_post(post)

    created.title = "Updated Title"
    created.content = "Updated Content"
    updated = await post_repository.update_post(created)

    assert updated.title == "Updated Title"
    assert updated.content == "Updated Content"

    # التحقق من قاعدة البيانات
    fetched = await post_repository.get_post_by_id(created.id)
    assert fetched.title == "Updated Title"
    assert fetched.content == "Updated Content"


@pytest.mark.integration
async def test_update_post_not_found_postgres(post_repository: PostRepositoryPostgresSQL):
    post = PostEntity(
        id="non-existent-post-id",
        title="Dummy Title",
        content="Dummy Content",
        author_id="author-dummy",
        author_role=Role.USER.value,
    )
    with pytest.raises(PostNotFound) as exc_info:
        await post_repository.update_post(post)
    assert exc_info.value.status_code == 404


@pytest.mark.integration
async def test_delete_post_success_postgres(post_repository: PostRepositoryPostgresSQL):
    post = PostEntity(
        title="To Be Deleted",
        content="Content To Be Deleted",
        author_id="author-pg-del",
        author_role=Role.USER.value,
    )
    created = await post_repository.create_post(post)

    result = await post_repository.delete_post(created.id)
    assert result is True

    # التأكد من عدم وجوده
    with pytest.raises(PostNotFound):
        await post_repository.get_post_by_id(created.id)


@pytest.mark.integration
async def test_delete_post_not_found_postgres(post_repository: PostRepositoryPostgresSQL):
    with pytest.raises(PostNotFound) as exc_info:
        await post_repository.delete_post("non-existent-delete-id")
    assert exc_info.value.status_code == 404


@pytest.mark.integration
async def test_list_posts_postgres(post_repository: PostRepositoryPostgresSQL):
    for i in range(3):
        post = PostEntity(
            title=f"List Post {i}",
            content=f"Content {i}",
            author_id=f"author-{i}",
            author_role=Role.USER.value,
        )
        await post_repository.create_post(post)

    posts = await post_repository.list_posts(limit=10, offset=0)
    assert len(posts) >= 3


@pytest.mark.integration
async def test_delete_posts_by_author_id_postgres(post_repository: PostRepositoryPostgresSQL):
    author_id = "author-pg-bulk-del"
    for i in range(3):
        post = PostEntity(
            title=f"Author Post {i}",
            content=f"Content {i}",
            author_id=author_id,
            author_role=Role.USER.value,
        )
        await post_repository.create_post(post)

    # حذف جميع بوستات الكاتب
    deleted_count = await post_repository.delete_posts_by_author_id(author_id)
    assert deleted_count >= 3

    # التحقق من أن الحذف المتتابع أزال جميع بوستات هذا الكاتب
    remaining_posts = await post_repository.list_posts(limit=100, offset=0)
    author_posts = [p for p in remaining_posts if p.author_id == author_id]
    assert len(author_posts) == 0
