from typing import Optional
import logging
from Core.Strings.RoleString import admin
from Core.errors.AuthErrors import AuthError, UserNotHaveRole
from Core.errors.GlobleErrors import ServerError
from Core.security.Jwt import verify_token
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)


class GetUserByIdUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, user_id: str, token: Optional[str] = None) -> UserEntity:
        try:
            if token is not None:
                payload = verify_token(token)
                role_val = getattr(payload, "role", None)
                if role_val != admin:
                    raise UserNotHaveRole()
            return await self.auth_repository.get_user_by_id(user_id)
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error getting user by id: {user_id}")
            raise ServerError(detail=str(e))
