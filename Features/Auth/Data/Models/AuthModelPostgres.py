from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from Core.Settings import SettingsApp
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status

setting = SettingsApp()


class Base(DeclarativeBase):
    pass


class AuthPostgresModel(Base):
    __tablename__ = setting.collection_users

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=Role.USER.value)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=Status.ACTIVE.value)
    created_at: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    )
    updated_at: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    )

    def to_entity(self) -> UserEntity:
        return UserEntity(
            id=self.id,
            name=self.name,
            email=self.email,
            password=self.password,
            role=self.role,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "AuthPostgresModel":
        role_val = entity.role.value if isinstance(entity.role, Role) else str(entity.role)
        status_val = entity.status.value if isinstance(entity.status, Status) else str(entity.status)
        return cls(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            password=entity.password,
            role=role_val,
            status=status_val,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthPostgresModel":
        if not data:
            return None
        role_val = data.get("role", Role.USER.value)
        if isinstance(role_val, Role):
            role_val = role_val.value
        status_val = data.get("status", Status.ACTIVE.value)
        if isinstance(status_val, Status):
            status_val = status_val.value

        return cls(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=role_val,
            status=status_val,
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
