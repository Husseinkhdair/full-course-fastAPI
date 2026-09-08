from Features.Auth.Domain.Entities.UserEntity import Role
from typing import Optional
from Features.Auth.Data.Models.AuthModelMongos import AuthMongosModel
import logging
from datetime import datetime, timezone
from bson import ObjectId

from Core.DataBase.MongoDb import collection_users
from Core.errors.AuthErrors import (
    AuthError,
    InvalidEmailOrPassword,
    UserAlredyExists,
    UserDoesNotExists,
)
from Core.errors.GlobleErrors import ServerError
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

from Core.security.Password import hash_password, verify_password

logger = logging.getLogger(__name__)


class AuthRepositoryMongoDB(AuthRepository):
    user_collection = collection_users

    async def create_user(self, email: str, name: str, password: str,role:Optional[Role]) -> UserEntity:
        try:
            logger.debug(f"creating user in mongodb with email: {email}")

            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            hashed_pwd = hash_password(password)

            user = AuthMongosModel(
                name=name,
                email=email,
                password=hashed_pwd,
                created_at=now_str,
                updated_at=now_str,
                role=role.value if role is not None else Role.USER.value
            )

            result = await self.user_collection.insert_one(user.to_dict())
            user.id = str(result.inserted_id)
            logger.info(f"user created successfully in mongodb with _id: {result.inserted_id}")
            return user.to_entity()

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error creating user in mongodb for email: {email}")
            raise ServerError(detail=str(e))

    async def login_user(self, email:str, password:str) -> UserEntity:
        try:
            logger.debug(f"logging in user with email: {email}")
            user_doc = await self.user_collection.find_one({"email": email})

            if not user_doc or not verify_password(password, user_doc.get("password", "")):
                logger.info(f"invalid credentials for email: {email}")
                raise InvalidEmailOrPassword()

            user = AuthMongosModel.from_dict(user_doc)
            user.id = str(user_doc.get("_id"))
            return user.to_entity()

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error logging in user: {email}")
            raise ServerError(detail=str(e))


    async def get_user_by_id(self, user_id:str) -> UserEntity:
        try:
            logger.debug(f"searching user in mongodb by id: {user_id}")
            query = [{"id": str(user_id)}, {"_id": str(user_id)}]
            if ObjectId.is_valid(str(user_id)):
                query.append({"_id": ObjectId(str(user_id))})

            user_doc = await self.user_collection.find_one({"$or": query})
            if not user_doc:
                logger.info(f"user not found in mongodb with id: {user_id}")
                raise UserDoesNotExists()

            user = AuthMongosModel.from_dict(user_doc)
            user.id = str(user_doc.get("_id"))
            return user.to_entity()

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error searching user by id: {user_id}")
            raise ServerError(detail=str(e))

    async def get_user_by_email(self, email: str) -> UserEntity:
        try:
            logger.debug(f"searching user in mongodb by email: {email}")
            user_doc = await self.user_collection.find_one({"email": email})
            if not user_doc:
                logger.info(f"user not found in mongodb with email: {email}")
                raise UserDoesNotExists()

            logger.debug(f"user found in mongodb with email: {email}")
            user = AuthMongosModel.from_dict(user_doc)
            user.id = str(user_doc.get("_id"))
            return user.to_entity()

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error searching user in mongodb by email: {email}")
            raise ServerError(detail=str(e))

    async def delete_user(self, user_id: str) -> bool:
        try:
            logger.debug(f"deleting user in mongodb by id: {user_id}")
            query = [{"id": str(user_id)}, {"_id": str(user_id)}]
            if ObjectId.is_valid(str(user_id)):
                query.append({"_id": ObjectId(str(user_id))})

            user_doc = await self.user_collection.find_one_and_delete({"$or": query})
            if not user_doc:
                logger.info(f"user not found to delete with id: {user_id}")
                raise UserDoesNotExists()

            logger.info(f"user deleted successfully with id: {user_id}")
            return True
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error deleting user by id: {user_id}")
            raise ServerError(detail=str(e))



            