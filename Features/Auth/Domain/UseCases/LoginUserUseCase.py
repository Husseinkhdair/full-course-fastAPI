from Features.Auth.Domain.Entities import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

class LoginUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, email:str , password:str) -> UserEntity:
        return await self.auth_repository.login_user(email, password)
