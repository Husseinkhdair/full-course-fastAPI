from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Presentation.tdo import LoginTDO, InfoUserTDO

class LoginUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, user: LoginTDO) -> InfoUserTDO:
        return await self.auth_repository.login_user(user)
