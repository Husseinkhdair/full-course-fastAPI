import logging
from typing import List, Optional
from bson import ObjectId
from Core.DataBase.MongoDb import collection_posts
from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Core.errors.PostErrors import PostError, PostNotFound
from Features.Post.Data.Models.PostModelMongos import PostMongosModel
from Features.Post.Domain.Entities.PostEntity import PostEntity
from Features.Post.Domain.Repository.PostRepository import PostRepository

logger = logging.getLogger(__name__)


class PostRepositoryMongoDB(PostRepository):
    post_collection = collection_posts

    def __init__(self, collection=None):
        if collection is not None:
            self.post_collection = collection

    async def create_post(self, post: PostEntity) -> PostEntity:
        try:
            logger.debug(f"creating post in mongodb: {post.title}")
            post_model = PostMongosModel.from_entity(post)
            result = await self.post_collection.insert_one(post_model.to_dict())
            post.id = str(result.inserted_id)
            logger.info(f"post created successfully in mongodb with _id: {post.id}")
            return post
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception(f"error creating post in mongodb: {post.title}")
            raise ServerError(detail=str(e))

    async def update_post(self, post: PostEntity) -> PostEntity:
        try:
            logger.debug(f"updating post in mongodb: {post.id}")
            query = [{"id": str(post.id)}, {"_id": str(post.id)}]
            if ObjectId.is_valid(str(post.id)):
                query.append({"_id": ObjectId(str(post.id))})

            update_data = {
                "title": post.title,
                "content": post.content,
                "updated_at": post.updated_at,
            }

            result = await self.post_collection.update_one(
                {"$or": query},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                raise PostNotFound()

            return post
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception(f"error updating post in mongodb: {post.id}")
            raise ServerError(detail=str(e))

    async def get_post_by_id(self, post_id: str) -> PostEntity:
        try:
            logger.debug(f"fetching post by id in mongodb: {post_id}")
            query = [{"id": str(post_id)}, {"_id": str(post_id)}]
            if ObjectId.is_valid(str(post_id)):
                query.append({"_id": ObjectId(str(post_id))})

            doc = await self.post_collection.find_one({"$or": query})
            if not doc:
                raise PostNotFound()

            model = PostMongosModel.from_dict(doc)
            return model.to_entity()
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception(f"error getting post by id in mongodb: {post_id}")
            raise ServerError(detail=str(e))

    async def delete_post(self, post_id: str) -> bool:
        try:
            logger.debug(f"deleting post in mongodb: {post_id}")
            query = [{"id": str(post_id)}, {"_id": str(post_id)}]
            if ObjectId.is_valid(str(post_id)):
                query.append({"_id": ObjectId(str(post_id))})

            result = await self.post_collection.delete_one({"$or": query})
            if result.deleted_count == 0:
                raise PostNotFound()

            return True
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception(f"error deleting post in mongodb: {post_id}")
            raise ServerError(detail=str(e))

    async def list_posts(self, limit: int = 10, offset: int = 0) -> List[PostEntity]:
        try:
            logger.debug(f"listing posts in mongodb with limit={limit}, offset={offset}")
            cursor = self.post_collection.find().skip(offset).limit(limit)
            posts: List[PostEntity] = []
            async for doc in cursor:
                model = PostMongosModel.from_dict(doc)
                posts.append(model.to_entity())
            return posts
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception("error listing posts in mongodb")
            raise ServerError(detail=str(e))

    async def delete_posts_by_author_id(self, author_id: str) -> int:
        try:
            logger.debug(f"deleting posts by author_id in mongodb: {author_id}")
            result = await self.post_collection.delete_many({"author_id": str(author_id)})
            return result.deleted_count
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception(f"error deleting posts for author in mongodb: {author_id}")
            raise ServerError(detail=str(e))
