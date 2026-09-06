import logging
from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)


class LoginUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, email: str, password: str) -> UserEntity:
        try:
            user = await self.auth_repository.login_user(email, password)

            role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
            payload = JWTPayload(id=user.id, email=user.email, role=role_str)
            user.token = generate_token(payload)

            return user

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error logging in user: {email}")
            raise ServerError(detail=str(e))
