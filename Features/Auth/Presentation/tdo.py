from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field

class CreateUserTDO(BaseModel):
    name: str = Field(..., description="Name", example="Hussein", min_length=1, max_length=255)
    email: EmailStr = Field(..., description="Email", example="hussein@gmail.com")
    password: str = Field(..., description="Password", example="password", min_length=6, max_length=16)

class LoginTDO(BaseModel):
    email: EmailStr = Field(..., description="Email", example="hussein@gmail.com")
    password: str = Field(..., description="Password", example="password", min_length=6, max_length=16)


class InfoUserTDO(BaseModel):
    user_id: Union[str, int] = Field(..., description="User ID", example=1)
    email: EmailStr = Field(..., description="Email", example="hussein@gmail.com")
    name: str = Field(..., description="Name", example="Hussein", min_length=1, max_length=255)
    created_at: Optional[str] = Field(None, description="Created At", example="2022-01-01 00:00:00")
    updated_at: Optional[str] = Field(None, description="Updated At", example="2022-01-01 00:00:00")
    role: Optional[str] = Field(None, description="Role", example="USER")
    status: Optional[str] = Field(None, description="Status", example="ACTIVE")
    token: Optional[str] = Field(None, description="Token", example="token")