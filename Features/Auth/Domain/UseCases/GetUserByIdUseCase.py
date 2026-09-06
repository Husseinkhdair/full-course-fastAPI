from Features.Auth.Domain.Entities import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

class GetUserByIdUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, user_id:str) -> UserEntity:
        return await self.auth_repository.get_user_by_id(user_id)
