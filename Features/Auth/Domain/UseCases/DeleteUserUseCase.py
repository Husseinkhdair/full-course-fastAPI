import logging
from typing import Optional, TYPE_CHECKING
from Core.errors.AuthErrors import AuthError, RoleError, UserNotHaveRole
from Core.errors.GlobleErrors import ServerError
from Core.security.Jwt import verify_token
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

if TYPE_CHECKING:
    from Features.Post.Domain.Repository.PostRepository import PostRepository

logger = logging.getLogger(__name__)


class DeleteUserUseCase:
    def __init__(
        self,
        auth_repository: AuthRepository,
        post_repository: Optional["PostRepository"] = None,
    ):
        self.auth_repository = auth_repository
        self.post_repository = post_repository

    async def execute(
        self,
        user_id: str,
        token: Optional[str]
    ) -> bool:
        try:
            user = verify_token(token)

            executor_role = user.role.value if isinstance(user.role, Role) else str(user.role)

            if executor_role not in [Role.ADMIN.value, Role.SUPERADMIN.value]:
                raise UserNotHaveRole()

            # جلب المستخدم الهدف للتحقق من رتبته وصلاحياته قبل الحذف
            target_user = await self.auth_repository.get_user_by_id(user_id)
            target_role = target_user.role.value if isinstance(target_user.role, Role) else str(target_user.role)

            # الأدمن لا يملك الصلاحية لحذف أدمن آخر أو سوبر أدمن
            if executor_role == Role.ADMIN.value and target_role in [Role.ADMIN.value, Role.SUPERADMIN.value]:
                raise RoleError(detail="Admin cannot delete another admin")

            # حذف جميع البوستات الخاصة بالمستخدم تلقائياً عند حذفه مهما كانت رتبته
            if self.post_repository:
                await self.post_repository.delete_posts_by_author_id(user_id)

            deleted = await self.auth_repository.delete_user(user_id)

            return deleted

        except AuthError:
            raise

        except Exception as e:
            logger.exception(f"error deleting user: {user_id}")
            raise ServerError(detail=str(e))