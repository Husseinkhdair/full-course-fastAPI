from typing import Optional
import logging

from Core.errors.AuthErrors import (
    AuthError,
    RoleError,
    UserAlredyExists,
    UserDoesNotExists,
)
from Core.errors.GlobleErrors import ServerError
from Core.security.Jwt import JWTPayload, generate_token, verify_token

from Features.Auth.Domain.Entities.UserEntity import Role, UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository


logger = logging.getLogger(__name__)


class CreateUserUseCase:

    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(
        self,
        email: str,
        name: str,
        password: str,
        token: Optional[str] = None,
        role: Optional[Role] = None,
    ) -> UserEntity:

        try:
            # ---------------------------------------
            # Check if user already exists
            # ---------------------------------------
            try:
                existing_user = await self.auth_repository.check_email_exists(
                    email
                )

                if existing_user:
                    raise UserAlredyExists()

            except UserDoesNotExists:
                pass

            # ---------------------------------------
            # Default role
            # ---------------------------------------
            requested_role = role or Role.USER

            # ---------------------------------------
            # No token
            # ---------------------------------------
            if not token:

                # Without authentication,
                # only normal USER can be created.
                if requested_role != Role.USER:
                    raise RoleError(
                        detail="you can only create a normal user"
                    )

                user = await self.auth_repository.create_user(
                    email,
                    name,
                    password,
                    Role.USER,
                )

            # ---------------------------------------
            # Token exists
            # ---------------------------------------
            else:

                # Get role from JWT
                check_role = verify_token(token).role

                # Convert string -> Role
                if isinstance(check_role, str):
                    check_role = Role(check_role)

                # ---------------------------------------
                # Normal USER
                # ---------------------------------------
                if check_role == Role.USER:

                    # USER can only create USER
                    if requested_role != Role.USER:
                        raise RoleError(
                            detail="user can only create normal users"
                        )

                # ---------------------------------------
                # ADMIN / SUPERADMIN
                # ---------------------------------------
                elif check_role in (
                    Role.ADMIN,
                    Role.SUPERADMIN,
                ):

                    # ADMIN and SUPERADMIN can create
                    # USER or ADMIN only.
                    if requested_role not in (
                        Role.USER,
                        Role.ADMIN,
                    ):
                        raise RoleError(
                            detail="you can only create user or admin"
                        )

                # ---------------------------------------
                # Invalid role
                # ---------------------------------------
                else:
                    raise RoleError(
                        detail="you are not authorized to create user"
                    )

                # ---------------------------------------
                # Create user
                # ---------------------------------------
                user = await self.auth_repository.create_user(
                    email,
                    name,
                    password,
                    requested_role,
                )

            # ---------------------------------------
            # Generate token for new user
            # ---------------------------------------
            user_role = (
                user.role.value
                if isinstance(user.role, Role)
                else str(user.role)
            )

            payload = JWTPayload(
                id=user.id,
                email=user.email,
                role=user_role,
            )

            user.token = generate_token(payload)

            return user

        # ---------------------------------------
        # Known authentication errors
        # ---------------------------------------
        except AuthError:
            raise

        # ---------------------------------------
        # Unexpected errors
        # ---------------------------------------
        except Exception as e:
            logger.exception(
                f"error creating user: {email}"
            )

            raise ServerError(
                detail=str(e)
            )