from Features.Auth.Domain.Entities.UserEntity import Role
from typing import Optional
from abc import ABC, abstractmethod
from Features.Auth.Domain.Entities.UserEntity import UserEntity


class AuthRepository(ABC):

    @abstractmethod
    async def create_user(self, email: str, name: str, password: str,role:Optional[Role] = None) -> UserEntity:
        pass

    @abstractmethod
    async def login_user(self, email: str, password: str) -> UserEntity:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> UserEntity:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserEntity:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass


    @abstractmethod
    async def check_email_exists(self, email: str) -> bool:
        pass




