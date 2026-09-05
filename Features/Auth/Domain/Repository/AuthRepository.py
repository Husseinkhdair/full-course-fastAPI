from typing import Union
from abc import ABC
from Features.Auth.Presentation.tdo import CreateUserTDO, InfoUserTDO, LoginTDO

class AuthRepository(ABC):

    async def create_user(self, user: CreateUserTDO) -> InfoUserTDO:
        pass

    async def login_user(self, user: LoginTDO) -> InfoUserTDO:
        pass

    async def get_user_by_id(self, user_id: Union[int, str]) -> InfoUserTDO:
        pass

    async def get_user_by_email(self, email: str) -> InfoUserTDO:
        pass

    async def delete_user(self, user_id: Union[int, str]) -> bool:
        pass

