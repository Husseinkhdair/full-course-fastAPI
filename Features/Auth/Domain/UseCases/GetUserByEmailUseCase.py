from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.Entities.UserEntity import UserEntity

class GetUserByEmailUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, email: str) -> UserEntity:
        return await self.auth_repository.get_user_by_email(email)
