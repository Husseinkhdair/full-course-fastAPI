import logging
from typing import List
from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Core.errors.PostErrors import PostError
from Features.Post.Domain.Entities.PostEntity import PostEntity
from Features.Post.Domain.Repository.PostRepository import PostRepository

logger = logging.getLogger(__name__)


class ListPostsUseCase:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository

    async def execute(self, limit: int = 10, offset: int = 0) -> List[PostEntity]:
        try:
            return await self.post_repository.list_posts(limit=limit, offset=offset)
        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception("error listing posts")
            raise ServerError(detail=str(e))
