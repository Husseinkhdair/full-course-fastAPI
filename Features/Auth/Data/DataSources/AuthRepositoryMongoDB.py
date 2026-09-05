import logging
from datetime import datetime, timezone
from typing import Union
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
from Features.Auth.Presentation.tdo import CreateUserTDO, InfoUserTDO, LoginTDO

from Core.security.Password import hash_password, verify_password

logger = logging.getLogger(__name__)


class AuthRepositoryMongoDB(AuthRepository):
    user_collection = collection_users

    async def create_user(self, user: CreateUserTDO) -> InfoUserTDO:
        try:
            logger.debug(f"creating user in mongodb with email: {user.email}")
            existing_user = await self.user_collection.find_one({"email": user.email})
            if existing_user:
                logger.info(f"user already exists with email: {user.email}")
                raise UserAlredyExists()

            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            hashed_pwd = hash_password(user.password)
            user_entity = UserEntity(
                name=user.name,
                email=user.email,
                password=hashed_pwd,
                created_at=now_str,
                updated_at=now_str
            )

            # Insert into MongoDB (MongoDB generates _id)
            result = await self.user_collection.insert_one(user_entity.to_dict())
            user_entity.id = str(result.inserted_id)
            logger.info(f"user created successfully in mongodb with _id: {user_entity.id}")

            return InfoUserTDO(
                user_id=user_entity.id,
                name=user_entity.name,
                email=user_entity.email,
                role=user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                status=user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                created_at=user_entity.created_at,
                updated_at=user_entity.updated_at
            )
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error creating user in mongodb for email: {user.email}")
            raise ServerError(detail=str(e))

    async def login_user(self, user: LoginTDO) -> InfoUserTDO:
        try:
            logger.debug(f"logging in user with email: {user.email}")
            user_doc = await self.user_collection.find_one({"email": user.email})
            if not user_doc or not verify_password(user.password, user_doc.get("password", "")):
                logger.info(f"invalid credentials for email: {user.email}")
                raise InvalidEmailOrPassword()

            user_entity = UserEntity.from_dict(user_doc)

            return InfoUserTDO(
                user_id=user_entity.id,
                name=user_entity.name,
                email=user_entity.email,
                role=user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                status=user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                created_at=user_entity.created_at,
                updated_at=user_entity.updated_at
            )
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error logging in user: {user.email}")
            raise ServerError(detail=str(e))


    async def get_user_by_id(self, user_id: Union[int, str]) -> InfoUserTDO:
        try:
            logger.debug(f"searching user in mongodb by id: {user_id}")
            query = [{"id": str(user_id)}, {"_id": str(user_id)}]
            if ObjectId.is_valid(str(user_id)):
                query.append({"_id": ObjectId(str(user_id))})

            user_doc = await self.user_collection.find_one({"$or": query})
            if not user_doc:
                logger.info(f"user not found in mongodb with id: {user_id}")
                raise UserDoesNotExists()

            user_entity = UserEntity.from_dict(user_doc)

            return InfoUserTDO(
                user_id=user_entity.id,
                name=user_entity.name,
                email=user_entity.email,
                role=user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                status=user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                created_at=user_entity.created_at,
                updated_at=user_entity.updated_at
            )
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error searching user by id: {user_id}")
            raise ServerError(detail=str(e))

    async def get_user_by_email(self, email: str) -> InfoUserTDO:
        try:
            logger.debug(f"searching user in mongodb by email: {email}")
            user_doc = await self.user_collection.find_one({"email": email})
            if not user_doc:
                logger.info(f"user not found in mongodb with email: {email}")
                raise UserDoesNotExists()

            logger.debug(f"user found in mongodb with email: {email}")
            user_entity = UserEntity.from_dict(user_doc)

            return InfoUserTDO(
                user_id=user_entity.id,
                name=user_entity.name,
                email=user_entity.email,
                role=user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                status=user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                created_at=user_entity.created_at,
                updated_at=user_entity.updated_at
            )

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error searching user in mongodb by email: {email}")
            raise ServerError(detail=str(e))


            