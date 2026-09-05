from Features.Auth.Presentation.tdo import LoginTDO
from abc import ABC
from Features.Auth.Presentation.tdo import CreateUserTDO,InfoUserTDO

class AuthRepository(ABC):

    def create_user(self,user:CreateUserTDO) -> InfoUserTDO:
        pass

    def login_user(self,user:LoginTDO) -> InfoUserTDO:
        pass

    def get_user_by_id(self,user_id:int) -> InfoUserTDO:
        pass
    