from datetime import datetime, timezone
import uuid
from typing import Any, Dict, Optional
from Features.Post.Domain.Entities.PostEntity import PostEntity


class PostMongosModel:
    def __init__(
        self,
        title: str,
        content: str,
        author_id: str,
        author_role: str,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self.id = str(id) if id is not None else str(uuid.uuid4())
        self.title = title
        self.content = content
        self.author_id = str(author_id)
        self.author_role = str(author_role)

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = created_at if created_at is not None else now_str
        self.updated_at = updated_at if updated_at is not None else now_str

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
    def from_entity(cls, entity: PostEntity) -> "PostMongosModel":
        return cls(
            id=entity.id,
            title=entity.title,
            content=entity.content,
            author_id=entity.author_id,
            author_role=entity.author_role,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "_id": self.id,
            "title": self.title,
            "content": self.content,
            "author_id": self.author_id,
            "author_role": self.author_role,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional["PostMongosModel"]:
        if not data:
            return None
        post_id = str(data.get("id") or data.get("_id") or "")
        return cls(
            id=post_id,
            title=data.get("title", ""),
            content=data.get("content", ""),
            author_id=str(data.get("author_id", "")),
            author_role=str(data.get("author_role", "user")),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
