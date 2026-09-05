import uuid
from enum import Enum
from typing import Optional, Union

class Role(Enum):
    ADMIN = "admin"
    USER = "user"

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"

class UserEntity:
    def __init__(
        self,
        name: str,
        email: str,
        password: str,
        role: Union[Role, str] = Role.USER,
        status: Union[Status, str] = Status.ACTIVE,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        id: Optional[Union[str, int]] = None
    ):
        self.id: str = str(id) if id is not None else str(uuid.uuid4())
        self.name: str = name
        self.email: str = email
        self.password: str = password
        self.role: Role = role if isinstance(role, Role) else Role(role)
        self.status: Status = status if isinstance(status, Status) else Status(status)
        self.created_at: Optional[str] = created_at
        self.updated_at: Optional[str] = updated_at

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email}, role={self.role.value}, status={self.status.value} , created_at={self.created_at}, updated_at={self.updated_at})"

    def __repr__(self):
        return self.__str__()



