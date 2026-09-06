from typing import Union
from abc import ABC
from Features.Auth.Presentation.tdo import CreateUserTDO, InfoUserTDO, LoginTDO
from Features.Auth.Domain.Entities.UserEntity import UserEntity
class AuthRepository(ABC):

    async def create_user(self, email:str , password:str, name:str) -> UserEntity:
        pass

    async def login_user(self, email:str , password:str) -> UserEntity:
        pass

    async def get_user_by_id(self, user_id:str) -> UserEntity:
        pass

    async def get_user_by_email(self, email:str) -> UserEntity:
        pass

    async def delete_user(self, id:str ) -> bool:
        pass

