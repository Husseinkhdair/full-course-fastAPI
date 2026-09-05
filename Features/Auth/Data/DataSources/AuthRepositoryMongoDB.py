from Features.Auth.Presentation.tdo import CreateUserTDO
from Features.Auth.Presentation.tdo import InfoUserTDO
from Features.Auth.Presentation.tdo import LoginTDO
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository



class AuthRepositoryMongoDB(AuthRepository):
    def create_user(self,user:CreateUserTDO) -> InfoUserTDO:
        pass

    def login_user(self,user:LoginTDO) -> InfoUserTDO:
        pass

    def get_user_by_id(self,user_id:int) -> InfoUserTDO:
        pass