from Features.Auth.Domain.Entities import UserEntity
from Features.Auth.Domain.Entities import UserEntity
from Core.errors.AuthErrors import UserDoesNotExists
from Core.DataBase.MongoDb import collection_users
from Features.Auth.Presentation.tdo import CreateUserTDO
from Features.Auth.Presentation.tdo import InfoUserTDO
from Features.Auth.Presentation.tdo import LoginTDO
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
import logging


logger = logging.getLogger(__name__)

class AuthRepositoryMongoDB(AuthRepository):
    user_collection = collection_users

    async def create_user(self,user:CreateUserTDO) -> InfoUserTDO:
        try:
            
        except:
            pass

    async def login_user(self,user:LoginTDO) -> InfoUserTDO:
        pass

    async def get_user_by_id(self,user_id:int) -> InfoUserTDO:
        pass

    async def get_user_by_email(self,email:str) -> InfoUserTDO:
        try:
            logger.debug("search user in mongodb")
            collection_user = self.user_collection.find_one({"email":email})
            if not collection_user:
                logger.debug(f"user not found in mongodb with email:{email}")
                raise UserDoesNotExists()
            
            logger.debug(f"user found in mongodb with email:{email}")
            user = UserEntity(**collection_user)
            user_tdo = InfoUserTDO(
                id=str(user.id),
                name=user.name,
                email=user.email,
                role=user.role
            )


            
            
            logger.debug("user found in mongodb")
            return user_tdo
            
        except Exception:
            logger.exception("error to search user in mongodb")
            