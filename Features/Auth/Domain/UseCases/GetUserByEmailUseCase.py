import logging
from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)


class GetUserByEmailUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, email: str) -> UserEntity:
        try:
            return await self.auth_repository.get_user_by_email(email)
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error getting user by email: {email}")
            raise ServerError(detail=str(e))
