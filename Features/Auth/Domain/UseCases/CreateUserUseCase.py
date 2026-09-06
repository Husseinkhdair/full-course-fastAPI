from Core.errors.AuthErrors import AuthError
from Core.errors.GlobleErrors import ServerError
from Core.errors.AuthErrors import UserAlredyExists
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.Entities.UserEntity import UserEntity
import logging

logger = logging.getLogger(__name__)

class CreateUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository
        

    async def execute(self,name:str ,email:str , password:str) -> UserEntity:
        try:
            is_user = await self.auth_repository.get_user_by_email(email)
            if is_user:
                raise UserAlredyExists()
            user = await self.auth_repository.create_user(email, password, name)
            return user

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error creating user: {email}")
            raise ServerError(detail=str(e))
