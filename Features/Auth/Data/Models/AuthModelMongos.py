from sqlalchemy.dialects.postgresql import Any
from ast import Dict
import uuid
from datetime import datetime, timezone
from typing import Optional
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status


class AuthMongosModel:
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
    ):
        self.id = id if id is not None else str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.status = status

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = created_at if created_at is not None else now_str
        self.updated_at = updated_at if updated_at is not None else now_str

    def to_entity(self) -> UserEntity:
        return UserEntity(
            id=self.id,
            name=self.name,
            email=self.email,
            password=self.password,
            role=self.role,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "AuthMongosModel":
        return cls(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            password=entity.password,
            role=entity.role,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role.value if isinstance(self.role, Role) else str(self.role),
            "status": self.status.value if isinstance(self.status, Status) else str(self.status),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthMongosModel":
        if not data:
            return None
        user_id = str(data.get("id") or data.get("_id") or "")
        return cls(
            id=user_id,
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=data.get("role", Role.USER),
            status=data.get("status", Status.ACTIVE),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
