from Features.Auth.Domain.Entities.UserEntity import Role,UserEntity
import logging
from Core.errors.AuthErrors import AuthError, UserNotHaveRole
from Core.errors.GlobleErrors import ServerError
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)


class GetUserByEmailUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, email: str, role:Role) -> UserEntity:
        try:
            if role == Role.USER :
                raise UserNotHaveRole()

            if role == Role.ADMIN or role == Role.SUPERADMIN :
                return await self.auth_repository.get_user_by_email(email)
            
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error getting user by email: {email}")
            raise ServerError(detail=str(e))
