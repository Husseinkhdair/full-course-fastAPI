from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Presentation.tdo import CreateUserTDO, InfoUserTDO

class CreateUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, user: CreateUserTDO) -> InfoUserTDO:
        return await self.auth_repository.create_user(user)
