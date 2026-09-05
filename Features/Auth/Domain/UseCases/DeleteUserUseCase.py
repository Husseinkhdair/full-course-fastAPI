from typing import Union
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Presentation.tdo import InfoUserTDO

class DeleteUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, user_id: Union[int, str]) -> InfoUserTDO:
        return await self.auth_repository.delete_user(user_id)
