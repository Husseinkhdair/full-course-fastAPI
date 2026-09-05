from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Presentation.tdo import InfoUserTDO

class GetUserByEmailUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, email: str) -> InfoUserTDO:
        return await self.auth_repository.get_user_by_email(email)
