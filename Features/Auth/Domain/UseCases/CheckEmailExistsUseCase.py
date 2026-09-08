import logging
from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)


class CheckEmailExistsUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, email: str) -> bool:
        try:
            return await self.auth_repository.check_email_exists(email)
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error checking email exists: {email}")
            raise ServerError(detail=str(e))
