import logging
from typing import List, Optional
from sqlalchemy import delete, select
from Core.DataBase.PostgresDB import SessionLocal
from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Core.errors.PostErrors import PostError, PostNotFound
from Features.Post.Data.Models.PostModelPostgres import PostPostgresModel
from Features.Post.Domain.Entities.PostEntity import PostEntity
from Features.Post.Domain.Repository.PostRepository import PostRepository

logger = logging.getLogger(__name__)


class PostRepositoryPostgresSQL(PostRepository):
    def __init__(self, db=None):
        self.db = db if db is not None else SessionLocal()

    async def create_post(self, post: PostEntity) -> PostEntity:
        try:
            logger.debug(f"creating post in postgresql: {post.title}")
            post_model = PostPostgresModel.from_entity(post)
            self.db.add(post_model)
            self.db.commit()
            self.db.refresh(post_model)
            return post_model.to_entity()
        except (AuthError, PostError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"error creating post in postgresql: {post.title}")
            raise ServerError(detail=str(e))

    async def update_post(self, post: PostEntity) -> PostEntity:
        try:
            logger.debug(f"updating post in postgresql: {post.id}")
            post_model = self.db.execute(
                select(PostPostgresModel).where(PostPostgresModel.id == str(post.id))
            ).scalars().first()

            if not post_model:
                raise PostNotFound()

            post_model.title = post.title
            post_model.content = post.content
            post_model.updated_at = post.updated_at

            self.db.commit()
            self.db.refresh(post_model)
            return post_model.to_entity()
        except (AuthError, PostError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"error updating post in postgresql: {post.id}")
            raise ServerError(detail=str(e))

    async def get_post_by_id(self, post_id: str) -> PostEntity:
        try:
            logger.debug(f"fetching post by id in postgresql: {post_id}")
            post_model = self.db.execute(
                select(PostPostgresModel).where(PostPostgresModel.id == str(post_id))
            ).scalars().first()

            if not post_model:
                raise PostNotFound()

            return post_model.to_entity()
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception(f"error getting post by id in postgresql: {post_id}")
            raise ServerError(detail=str(e))

    async def delete_post(self, post_id: str) -> bool:
        try:
            logger.debug(f"deleting post in postgresql: {post_id}")
            post_model = self.db.execute(
                select(PostPostgresModel).where(PostPostgresModel.id == str(post_id))
            ).scalars().first()

            if not post_model:
                raise PostNotFound()

            self.db.delete(post_model)
            self.db.commit()
            return True
        except (AuthError, PostError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"error deleting post in postgresql: {post_id}")
            raise ServerError(detail=str(e))

    async def list_posts(self, limit: int = 10, offset: int = 0) -> List[PostEntity]:
        try:
            logger.debug(f"listing posts in postgresql with limit={limit}, offset={offset}")
            posts_models = self.db.execute(
                select(PostPostgresModel).order_by(PostPostgresModel.created_at.desc()).offset(offset).limit(limit)
            ).scalars().all()

            return [model.to_entity() for model in posts_models]
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception("error listing posts in postgresql")
            raise ServerError(detail=str(e))

    async def delete_posts_by_author_id(self, author_id: str) -> int:
        try:
            logger.debug(f"deleting posts by author_id in postgresql: {author_id}")
            result = self.db.execute(
                delete(PostPostgresModel).where(PostPostgresModel.author_id == str(author_id))
            )
            self.db.commit()
            return result.rowcount or 0
        except (AuthError, PostError):
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"error deleting posts for author in postgresql: {author_id}")
            raise ServerError(detail=str(e))
