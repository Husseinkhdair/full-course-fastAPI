import logging
import uuid
from datetime import datetime, timezone
from typing import Union

from Core.DataBase.PostgreDB import get_postgres_pool, init_postgres_db
try:
    from asyncpg.exceptions import UndefinedTableError
except ImportError:
    UndefinedTableError = Exception

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


class AuthRepositoryPostgreSQL(AuthRepository):
    def __init__(self, pool=None):
        self.pool = pool

    async def _get_pool(self):
        if self.pool is not None:
            return self.pool
        return await get_postgres_pool()

    async def create_user(self, user: CreateUserTDO) -> InfoUserTDO:
        try:
            logger.debug(f"creating user in postgresql with email: {user.email}")
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                existing = await conn.fetchrow("SELECT email FROM users WHERE email = $1", user.email)
                if existing:
                    logger.info(f"user already exists in postgresql with email: {user.email}")
                    raise UserAlredyExists()

                now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                hashed_pwd = hash_password(user.password)
                generated_id = str(uuid.uuid4())

                user_entity = UserEntity(
                    id=generated_id,
                    name=user.name,
                    email=user.email,
                    password=hashed_pwd,
                    created_at=now_str,
                    updated_at=now_str
                )

                await conn.execute(
                    """
                    INSERT INTO users (id, name, email, password, role, status, created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """,
                    user_entity.id,
                    user_entity.name,
                    user_entity.email,
                    user_entity.password,
                    user_entity.role.value if hasattr(user_entity.role, "value") else str(user_entity.role),
                    user_entity.status.value if hasattr(user_entity.status, "value") else str(user_entity.status),
                    user_entity.created_at,
                    user_entity.updated_at
                )
                logger.info(f"user created successfully in postgresql with id: {user_entity.id}")

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
        except UndefinedTableError:
            logger.info("Table 'users' does not exist in PostgreSQL. Initializing table now...")
            pool = await self._get_pool()
            await init_postgres_db(pool)
            return await self.create_user(user)
        except Exception as e:
            logger.exception(f"error creating user in postgresql for email: {user.email}")
            raise ServerError(detail=str(e))

    async def login_user(self, user: LoginTDO) -> InfoUserTDO:
        try:
            logger.debug(f"logging in user in postgresql with email: {user.email}")
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", user.email)
                if not row or not verify_password(user.password, row["password"]):
                    logger.info(f"invalid credentials in postgresql for email: {user.email}")
                    raise InvalidEmailOrPassword()

                user_dict = dict(row)
                user_entity = UserEntity.from_dict(user_dict)

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
        except UndefinedTableError:
            logger.info("Table 'users' does not exist in PostgreSQL. Initializing table now...")
            pool = await self._get_pool()
            await init_postgres_db(pool)
            return await self.login_user(user)
        except Exception as e:
            logger.exception(f"error logging in user in postgresql: {user.email}")
            raise ServerError(detail=str(e))

    async def get_user_by_id(self, user_id: Union[int, str]) -> InfoUserTDO:
        try:
            logger.debug(f"searching user in postgresql by id: {user_id}")
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", str(user_id))
                if not row:
                    logger.info(f"user not found in postgresql with id: {user_id}")
                    raise UserDoesNotExists()

                user_dict = dict(row)
                user_entity = UserEntity.from_dict(user_dict)

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
        except UndefinedTableError:
            logger.info("Table 'users' does not exist in PostgreSQL. Initializing table now...")
            pool = await self._get_pool()
            await init_postgres_db(pool)
            return await self.get_user_by_id(user_id)
        except Exception as e:
            logger.exception(f"error searching user by id in postgresql: {user_id}")
            raise ServerError(detail=str(e))

    async def get_user_by_email(self, email: str) -> InfoUserTDO:
        try:
            logger.debug(f"searching user in postgresql by email: {email}")
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
                if not row:
                    logger.info(f"user not found in postgresql with email: {email}")
                    raise UserDoesNotExists()

                user_dict = dict(row)
                user_entity = UserEntity.from_dict(user_dict)

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
        except UndefinedTableError:
            logger.info("Table 'users' does not exist in PostgreSQL. Initializing table now...")
            pool = await self._get_pool()
            await init_postgres_db(pool)
            return await self.get_user_by_email(email)
        except Exception as e:
            logger.exception(f"error searching user by email in postgresql: {email}")
            raise ServerError(detail=str(e))

    async def delete_user(self, user_id: Union[int, str]) -> bool:
        try:
            logger.debug(f"deleting user in postgresql by id: {user_id}")
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow("DELETE FROM users WHERE id = $1 RETURNING id", str(user_id))
                if not row:
                    logger.info(f"user not found to delete in postgresql with id: {user_id}")
                    raise UserDoesNotExists()

                logger.info(f"user deleted successfully in postgresql with id: {user_id}")
                return True
        except AuthError:
            raise
        except UndefinedTableError:
            logger.info("Table 'users' does not exist in PostgreSQL. Initializing table now...")
            pool = await self._get_pool()
            await init_postgres_db(pool)
            return await self.delete_user(user_id)
        except Exception as e:
            logger.exception(f"error deleting user by id in postgresql: {user_id}")
            raise ServerError(detail=str(e))
