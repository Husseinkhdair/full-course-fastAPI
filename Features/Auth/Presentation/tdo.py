from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field

class CreateUserTDO(BaseModel):
    name: str = Field(..., description="Name", json_schema_extra={"example": "Hussein"}, min_length=1, max_length=255)
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    password: str = Field(..., description="Password", json_schema_extra={"example": "password"}, min_length=6, max_length=16)

class LoginTDO(BaseModel):
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    password: str = Field(..., description="Password", json_schema_extra={"example": "password"}, min_length=6, max_length=16)


class InfoUserTDO(BaseModel):
    user_id: Union[str, int] = Field(..., description="User ID", json_schema_extra={"example": 1})
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    name: str = Field(..., description="Name", json_schema_extra={"example": "Hussein"}, min_length=1, max_length=255)

    created_at: Optional[str] = Field(None, description="Created At", json_schema_extra={"example": "2022-01-01 00:00:00"})
    updated_at: Optional[str] = Field(None, description="Updated At", json_schema_extra={"example": "2022-01-01 00:00:00"})
    role: Optional[str] = Field(None, description="Role", json_schema_extra={"example": "USER"})
    status: Optional[str] = Field(None, description="Status", json_schema_extra={"example": "ACTIVE"})
    token: Optional[str] = Field(None, description="Token", json_schema_extra={"example": "token"})