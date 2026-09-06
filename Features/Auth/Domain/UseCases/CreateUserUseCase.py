from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.Entities.UserEntity import UserEntity

class CreateUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self,name:str ,email:str , password:str) -> UserEntity:
        return await self.auth_repository.create_user(email, password, name)
