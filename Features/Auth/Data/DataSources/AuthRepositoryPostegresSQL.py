import logging
import uuid
from datetime import datetime, timezone
from typing import Union

from sqlalchemy import select

from Core.DataBase.PostgresDB import SessionLocal
from Core.errors.AuthErrors import (
    AuthError,
    InvalidEmailOrPassword,
    UserAlredyExists,
    UserDoesNotExists,
)
from Core.errors.GlobleErrors import ServerError
from Core.security.Password import hash_password, verify_password
from Features.Auth.Data.Models.AuthModelPostgres import AuthPostgresModel
from Features.Auth.Domain.Entities.UserEntity import Role, Status
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Presentation.tdo import CreateUserTDO, InfoUserTDO, LoginTDO

logger = logging.getLogger(__name__)


class AuthRepositoryPostgresSQl(AuthRepository):

    def __init__(self, db=None):
        self.db = db if db is not None else SessionLocal()

    async def create_user(self, user: CreateUserTDO) -> InfoUserTDO:
        try:
            logger.debug(f"creating user in postgresql with email: {user.email}")

            existing = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.email == user.email)
            ).scalars().first()

            if existing:
                logger.info(f"user already exists with email: {user.email}")
                raise UserAlredyExists()

            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            hashed_pwd = hash_password(user.password)
            generated_id = str(uuid.uuid4())

            usernew = AuthPostgresModel(
                id=generated_id,
                email=user.email,
                name=user.name,
                password=hashed_pwd,
                role=Role.USER.value,
                status=Status.ACTIVE.value,
                created_at=now_str,
                updated_at=now_str,
            )

            self.db.add(usernew)
            self.db.commit()
            self.db.refresh(usernew)

            logger.info(f"user created successfully in postgresql with id: {usernew.id}")

            user_entity = usernew.to_entity()

            return InfoUserTDO(
                user_id=user_entity.id,
                name=user_entity.name,
                email=user_entity.email,
                role=user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                status=user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                created_at=user_entity.created_at,
                updated_at=user_entity.updated_at,
            )

        except AuthError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"error creating user in postgresql for email: {user.email}")
            raise ServerError(detail=str(e))

    async def login_user(self, user: LoginTDO) -> InfoUserTDO:
        try:
            logger.debug(f"logging in user with email: {user.email}")
            db_user = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.email == user.email)
            ).scalars().first()

            if not db_user or not verify_password(user.password, db_user.password):
                logger.info(f"invalid credentials for email: {user.email}")
                raise InvalidEmailOrPassword()

            user_entity = db_user.to_entity()

            return InfoUserTDO(
                user_id=user_entity.id,
                name=user_entity.name,
                email=user_entity.email,
                role=user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                status=user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                created_at=user_entity.created_at,
                updated_at=user_entity.updated_at,
            )
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error logging in user in postgresql: {user.email}")
            raise ServerError(detail=str(e))

    async def get_user_by_id(self, user_id: Union[int, str]) -> InfoUserTDO:
        try:
            logger.debug(f"searching user in postgresql by id: {user_id}")
            db_user = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.id == str(user_id))
            ).scalars().first()

            if not db_user:
                logger.info(f"user not found in postgresql with id: {user_id}")
                raise UserDoesNotExists()

            user_entity = db_user.to_entity()

            return InfoUserTDO(
                user_id=user_entity.id,
                name=user_entity.name,
                email=user_entity.email,
                role=user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                status=user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                created_at=user_entity.created_at,
                updated_at=user_entity.updated_at,
            )
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error searching user by id in postgresql: {user_id}")
            raise ServerError(detail=str(e))

    async def get_user_by_email(self, email: str) -> InfoUserTDO:
        try:
            logger.debug(f"searching user in postgresql by email: {email}")
            db_user = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.email == email)
            ).scalars().first()

            if not db_user:
                logger.info(f"user not found in postgresql with email: {email}")
                raise UserDoesNotExists()

            user_entity = db_user.to_entity()

            return InfoUserTDO(
                user_id=user_entity.id,
                name=user_entity.name,
                email=user_entity.email,
                role=user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                status=user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                created_at=user_entity.created_at,
                updated_at=user_entity.updated_at,
            )
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error searching user by email in postgresql: {email}")
            raise ServerError(detail=str(e))

    async def delete_user(self, user_id: Union[int, str]) -> bool:
        try:
            logger.debug(f"deleting user in postgresql by id: {user_id}")
            db_user = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.id == str(user_id))
            ).scalars().first()

            if not db_user:
                logger.info(f"user not found to delete in postgresql with id: {user_id}")
                raise UserDoesNotExists()

            self.db.delete(db_user)
            self.db.commit()

            logger.info(f"user deleted successfully in postgresql with id: {user_id}")
            return True
        except AuthError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"error deleting user by id in postgresql: {user_id}")
            raise ServerError(detail=str(e))
