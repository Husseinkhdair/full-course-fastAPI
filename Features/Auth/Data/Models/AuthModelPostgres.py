import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
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
    created_at: Mapped[str] = mapped_column(String(100), nullable=False, default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: Mapped[str] = mapped_column(String(100), nullable=False, default=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))

    def __init__(
        self, 
        name: str, 
        email: str, 
        password: str, 
        role: Role = Role.USER, 
        status: Status = Status.ACTIVE, 
        created_at: Optional[str] = None, 
        updated_at: Optional[str] = None, 
        id: Optional[str] = None
    ):
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.id = id if id else str(uuid.uuid4())
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.status = status
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

    