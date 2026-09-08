import logging
from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Core.errors.PostErrors import PostError
from Features.Post.Domain.Entities.PostEntity import PostEntity
from Features.Post.Domain.Repository.PostRepository import PostRepository

logger = logging.getLogger(__name__)


class GetPostByIdUseCase:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository

    async def execute(self, post_id: str) -> PostEntity:
        try:
            return await self.post_repository.get_post_by_id(post_id)
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception(f"error getting post by id: {post_id}")
            raise ServerError(detail=str(e))
