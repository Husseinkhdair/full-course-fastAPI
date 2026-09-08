from typing import Optional
from pydantic import BaseModel, Field
from Features.Post.Domain.Entities.PostEntity import PostEntity


class CreatePostTDO(BaseModel):
    title: str = Field(..., description="Post Title", min_length=1, max_length=255, json_schema_extra={"example": "First Post"})
    content: str = Field(..., description="Post Content", min_length=1, json_schema_extra={"example": "This is the content of the post."})


class UpdatePostTDO(BaseModel):
    title: Optional[str] = Field(None, description="Post Title", min_length=1, max_length=255, json_schema_extra={"example": "Updated Post Title"})
    content: Optional[str] = Field(None, description="Post Content", min_length=1, json_schema_extra={"example": "Updated content."})


class InfoPostTDO(BaseModel):
    id: str = Field(..., description="Post ID", json_schema_extra={"example": "uuid-or-objectid"})
    title: str = Field(..., description="Post Title", json_schema_extra={"example": "First Post"})
    content: str = Field(..., description="Post Content", json_schema_extra={"example": "This is the content."})
    author_id: str = Field(..., description="Author User ID", json_schema_extra={"example": "author-user-id"})
    author_role: str = Field(..., description="Author Role at creation", json_schema_extra={"example": "user"})
    created_at: Optional[str] = Field(None, description="Created Timestamp")
    updated_at: Optional[str] = Field(None, description="Updated Timestamp")

    @classmethod
    def from_entity(cls, entity: PostEntity) -> "InfoPostTDO":
        return cls(
            id=str(entity.id),
            title=entity.title,
            content=entity.content,
            author_id=str(entity.author_id),
            author_role=str(entity.author_role),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
