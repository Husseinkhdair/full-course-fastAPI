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
        self.id: Optional[str] = str(id) if id is not None else None
        self.name: str = name
        self.email: str = email
        self.password: str = password
        self.role: Role = role if isinstance(role, Role) else Role(role)
        self.status: Status = status if isinstance(status, Status) else Status(status)
        self.created_at: Optional[str] = created_at
        self.updated_at: Optional[str] = updated_at

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role.value if isinstance(self.role, Role) else self.role,
            "status": self.status.value if isinstance(self.status, Status) else self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if self.id is not None:
            data["id"] = self.id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "UserEntity":
        user_id = data.get("id") or (str(data.get("_id")) if data.get("_id") else None)
        return cls(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            role=data.get("role", Role.USER),
            status=data.get("status", Status.ACTIVE),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            id=user_id
        )

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email}, role={self.role.value}, status={self.status.value}, created_at={self.created_at}, updated_at={self.updated_at})"

    def __repr__(self):
        return self.__str__()




