from datetime import datetime, timezone
import uuid
from typing import Optional
from Features.Auth.Domain.Entities.UserEntity import Role


class PostEntity:
    def __init__(
        self,
        title: str,
        content: str,
        author_id: str,
        author_role: str = Role.USER.value,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        id: Optional[str] = None,
    ):
        self.id = str(id) if id is not None else str(uuid.uuid4())
        self.title = title
        self.content = content
        self.author_id = str(author_id)
        self.author_role = author_role.value if isinstance(author_role, Role) else str(author_role)

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = created_at if created_at is not None else now_str
        self.updated_at = updated_at if updated_at is not None else now_str

    def __str__(self):
        return f"Post(id={self.id}, title={self.title}, author_id={self.author_id}, author_role={self.author_role})"

    def __repr__(self):
        return self.__str__()
