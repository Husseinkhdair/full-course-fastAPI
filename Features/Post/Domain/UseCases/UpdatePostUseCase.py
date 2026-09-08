from datetime import datetime, timezone
import logging
from typing import Optional
from Core.errors.AuthErrors import AuthError, UserDoesNotExists
from Core.errors.GlobleErrors import ServerError
from Core.errors.PostErrors import PostError, PostPermissionDenied
from Core.security.Jwt import verify_token
from Features.Auth.Domain.Entities.UserEntity import Role, Status
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Post.Domain.Entities.PostEntity import PostEntity
from Features.Post.Domain.Repository.PostRepository import PostRepository

logger = logging.getLogger(__name__)


class UpdatePostUseCase:
    def __init__(
        self,
        post_repository: PostRepository,
        auth_repository: Optional[AuthRepository] = None,
    ):
        self.post_repository = post_repository
        self.auth_repository = auth_repository

    async def execute(
        self,
        post_id: str,
        token: Optional[str],
        title: Optional[str] = None,
        content: Optional[str] = None,
    ) -> PostEntity:
        try:
            user = verify_token(token)
            executor_id = str(user.id)
            executor_role = user.role.value if isinstance(user.role, Role) else str(user.role)

            # التحقق من أن المستخدم موجود في قاعدة البيانات وحالته غير محذوف
            if self.auth_repository:
                executor = await self.auth_repository.get_user_by_id(executor_id)
                status_val = executor.status.value if hasattr(executor.status, "value") else str(executor.status)
                if status_val.lower() == Status.DELETED.value.lower():
                    raise UserDoesNotExists()
                executor_role = executor.role.value if hasattr(executor.role, "value") else str(executor.role)

            post = await self.post_repository.get_post_by_id(post_id)

            # فحص الصلاحيات الهرمية
            is_author = (executor_id == str(post.author_id))

            if not is_author:
                # المستخدم العادي لا يمكنه تعديل بوست مستخدم آخر
                if executor_role == Role.USER.value:
                    raise PostPermissionDenied("Users cannot update other users' posts")

                # المشرف (Admin) لا يمكنه تعديل بوست مشرف آخر أو سوبر أدمن
                if executor_role == Role.ADMIN.value:
                    if post.author_role in [Role.ADMIN.value, Role.SUPERADMIN.value]:
                        raise PostPermissionDenied("Admins cannot update posts of other admins or superadmins")

                # السوبر أدمن مسموح له بتعديل أي بوست

            # تحديث الحقول
            if title is not None:
                post.title = title
            if content is not None:
                post.content = content

            post.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            updated_post = await self.post_repository.update_post(post)
            return updated_post

        except (AuthError, PostError):
            raise
        except Exception as e:
            logger.exception(f"error updating post: {post_id}")
            raise ServerError(detail=str(e))
