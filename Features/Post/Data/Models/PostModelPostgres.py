from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from Core.Settings import SettingsApp
from Features.Auth.Data.Models.AuthModelPostgres import Base
from Features.Post.Domain.Entities.PostEntity import PostEntity

settings = SettingsApp()


class PostPostgresModel(Base):
    __tablename__ = "Posts"

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[str] = mapped_column(String(255), nullable=False)
    author_role: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(100), nullable=False)

    def to_entity(self) -> PostEntity:
        return PostEntity(
            id=self.id,
            title=self.title,
            content=self.content,
            author_id=self.author_id,
            author_role=self.author_role,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @classmethod
    def from_entity(cls, entity: PostEntity) -> "PostPostgresModel":
        return cls(
            id=entity.id,
            title=entity.title,
            content=entity.content,
            author_id=entity.author_id,
            author_role=entity.author_role,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
