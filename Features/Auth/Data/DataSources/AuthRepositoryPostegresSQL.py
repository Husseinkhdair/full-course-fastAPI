from typing import Optional
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
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)


class AuthRepositoryPostgresSQl(AuthRepository):

    def __init__(self, db=None):
        self.db = db if db is not None else SessionLocal()

    async def create_user(self, email: str, name: str, password: str,role:Optional[Role]) -> UserEntity:
        try:
            logger.debug(f"creating user in postgresql with email: {email}")

            existing = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.email == email)
            ).scalars().first()

            if existing:
                logger.info(f"user already exists with email: {email}")
                raise UserAlredyExists()

            now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            hashed_pwd = hash_password(password)

            usernew = AuthPostgresModel(
                email=email,
                name=name,
                password=hashed_pwd,
                role=Role.USER.value if role is None else role.value,
                status=Status.ACTIVE.value,
                created_at=now_str,
                updated_at=now_str,
                
            )

            self.db.add(usernew)
            self.db.commit()
            self.db.refresh(usernew)

            logger.info(f"user created successfully in postgresql with id: {usernew.id}")

            return usernew.to_entity()

        except AuthError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"error creating user in postgresql for email: {email}")
            raise ServerError(detail=str(e))

    async def login_user(self, email: str, password: str) -> UserEntity:
        try:
            logger.debug(f"logging in user with email: {email}")
            db_user = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.email == email)
            ).scalars().first()

            if not db_user or not verify_password(password, db_user.password):
                logger.info(f"invalid credentials for email: {email}")
                raise InvalidEmailOrPassword()

            return db_user.to_entity()

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error logging in user in postgresql: {email}")
            raise ServerError(detail=str(e))

    async def get_user_by_id(self, user_id: str) -> UserEntity:
        try:
            logger.debug(f"searching user in postgresql by id: {user_id}")
            db_user = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.id == str(user_id))
            ).scalars().first()

            if not db_user:
                logger.info(f"user not found in postgresql with id: {user_id}")
                raise UserDoesNotExists()

            return db_user.to_entity()

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error searching user by id in postgresql: {user_id}")
            raise ServerError(detail=str(e))

    async def get_user_by_email(self, email: str) -> UserEntity:
        try:
            logger.debug(f"searching user in postgresql by email: {email}")
            db_user = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.email == email)
            ).scalars().first()

            if not db_user:
                logger.info(f"user not found in postgresql with email: {email}")
                raise UserDoesNotExists()

            return db_user.to_entity()

        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error searching user by email in postgresql: {email}")
            raise ServerError(detail=str(e))

    async def delete_user(self, user_id: str) -> bool:
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

