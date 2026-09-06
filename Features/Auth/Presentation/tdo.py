from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field
from Features.Auth.Domain.Entities.UserEntity import UserEntity


class CreateUserTDO(BaseModel):
    name: str = Field(..., description="Name", json_schema_extra={"example": "Hussein"}, min_length=1, max_length=255)
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    password: str = Field(..., description="Password", json_schema_extra={"example": "password"}, min_length=6, max_length=16)


class LoginTDO(BaseModel):
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    password: str = Field(..., description="Password", json_schema_extra={"example": "password"}, min_length=6, max_length=16)


class InfoUserTDO(BaseModel):
    user_id: Union[str, int] = Field(..., description="User ID", json_schema_extra={"example": "123"})
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    name: str = Field(..., description="Name", json_schema_extra={"example": "Hussein"}, min_length=1, max_length=255)

    created_at: Optional[str] = Field(None, description="Created At", json_schema_extra={"example": "2022-01-01 00:00:00"})
    updated_at: Optional[str] = Field(None, description="Updated At", json_schema_extra={"example": "2022-01-01 00:00:00"})
    role: Optional[str] = Field(None, description="Role", json_schema_extra={"example": "user"})
    status: Optional[str] = Field(None, description="Status", json_schema_extra={"example": "active"})
    token: Optional[str] = Field(None, description="Token", json_schema_extra={"example": "token"})

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "InfoUserTDO":
        if not entity:
            return None
        role_val = entity.role.value if hasattr(entity.role, "value") else str(entity.role)
        status_val = entity.status.value if hasattr(entity.status, "value") else str(entity.status)
        return cls(
            user_id=str(entity.id),
            name=entity.name,
            email=entity.email,
            role=role_val,
            status=status_val,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            token=getattr(entity, "token", None),
        )
