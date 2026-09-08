import logging
from typing import Optional
from Core.errors.AuthErrors import AuthError, UserNotHaveRole
from Core.errors.GlobleErrors import ServerError
from Core.security.Jwt import verify_token
from Features.Auth.Domain.Entities.UserEntity import Role
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)


class DeleteUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(
        self,
        user_id: str,
        token: Optional[str]
    ) -> bool:
        try:
            user = verify_token(token)

            role_val = user.role.value if isinstance(user.role, Role) else str(user.role)

            if role_val not in [Role.ADMIN.value, Role.SUPERADMIN.value]:
                raise UserNotHaveRole()

            deleted = await self.auth_repository.delete_user(user_id)

            return deleted

        except AuthError:
            raise

        except Exception as e:
            logger.exception(f"error deleting user: {user_id}")
            raise ServerError(detail=str(e))