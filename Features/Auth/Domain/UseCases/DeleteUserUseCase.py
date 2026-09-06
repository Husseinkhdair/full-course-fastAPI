import logging
from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)


class DeleteUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, user_id: str) -> bool:
        try:
            return await self.auth_repository.delete_user(user_id)
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error deleting user: {user_id}")
            raise ServerError(detail=str(e))

