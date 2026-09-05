from Core.Settings import SettingsApp
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

setting = SettingsApp()

class Base(DeclarativeBase):
    pass


class AuthPostgresModel(Base):
    __tablename__ = setting.collection_users

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(100), nullable=False)

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


