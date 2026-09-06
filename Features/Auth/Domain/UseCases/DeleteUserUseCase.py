from typing import Union
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

class DeleteUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, id:str ) -> bool:
        return await self.auth_repository.delete_user(id)

