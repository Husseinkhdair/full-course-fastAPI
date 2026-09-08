import logging
from typing import Optional
from Core.errors.AuthErrors import AuthError, InvalidToken, UserDoesNotExists
from Core.errors.GlobleErrors import ServerError
from Core.security.Jwt import verify_token
from Features.Auth.Domain.Entities.UserEntity import Role, Status
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Post.Domain.Entities.PostEntity import PostEntity
from Features.Post.Domain.Repository.PostRepository import PostRepository

logger = logging.getLogger(__name__)


class CreatePostUseCase:
    def __init__(
        self,
        post_repository: PostRepository,
        auth_repository: Optional[AuthRepository] = None,
    ):
        self.post_repository = post_repository
        self.auth_repository = auth_repository

    async def execute(
        self,
        title: str,
        content: str,
        token: Optional[str],
    ) -> PostEntity:
        try:
            user = verify_token(token)
            author_id = str(user.id)
            author_role = user.role.value if isinstance(user.role, Role) else str(user.role)

            # التحقق من أن المستخدم موجود في قاعدة البيانات وحالته غير محذوف
            if self.auth_repository:
                executor = await self.auth_repository.get_user_by_id(author_id)
                status_val = executor.status.value if hasattr(executor.status, "value") else str(executor.status)
                if status_val.lower() == Status.DELETED.value.lower():
                    raise UserDoesNotExists()
                author_role = executor.role.value if hasattr(executor.role, "value") else str(executor.role)

            post = PostEntity(
                title=title,
                content=content,
                author_id=author_id,
                author_role=author_role,
            )

            created_post = await self.post_repository.create_post(post)
            return created_post

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error creating post: {title}")
            raise ServerError(detail=str(e))
