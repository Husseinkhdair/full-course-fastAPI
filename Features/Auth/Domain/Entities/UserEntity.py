from Core.Strings.RoleString import admin,user,active,inactive,deleted,superAdmin
from datetime import datetime, timezone
import uuid
from enum import Enum
from typing import Optional


class Role(Enum):
    ADMIN = admin
    USER = user
    SUPERADMIN = superAdmin



class Status(Enum):
    ACTIVE   = active
    INACTIVE = inactive
    DELETED  = deleted


class UserEntity:
    def __init__(
        self,
        name: str,
        email: str,
        password: str,
        role: Role = Role.USER,
        status: Status = Status.ACTIVE,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        id: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.status = status

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = created_at if created_at is not None else now_str
        self.updated_at = updated_at if updated_at is not None else now_str
        self.id = id if id is not None else str(uuid.uuid4())
        self.token = token if token is not None else None


    def __str__(self):
        role_str = self.role.value if isinstance(self.role, Role) else str(self.role)
        status_str = self.status.value if isinstance(self.status, Status) else str(self.status)
        return (
            f"User(id={self.id}, name={self.name}, email={self.email}, "
            f"role={role_str}, status={status_str}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )

    def __repr__(self):
        return self.__str__()
