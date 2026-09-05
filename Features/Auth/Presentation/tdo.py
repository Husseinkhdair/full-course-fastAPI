from typing import Optional
from fastapi import File
from pydantic import BaseModel, EmailStr

class CreateUserTDO(BaseModel):
    name: str = File(..., description="Name",example="Hussein",min_length=1,max_length=255)
    email: EmailStr = File(..., description="Email",example="hussein@gmail.com")
    password: str = File(..., description="Password",example="password",min_length=6,max_length=16)

class LoginTDO(BaseModel):
    email: EmailStr = File(..., description="Email",example="hussein@gmail.com")
    password: str = File(..., description="Password",example="password",min_length=6,max_length=16)


class InfoUserTDO(BaseModel):
    user_id: int = File(..., description="User ID",example=1)
    email: EmailStr = File(..., description="Email",example="[EMAIL_ADDRESS]")
    name: str = File(..., description="Name",example="Hussein",min_length=1,max_length=255)
    created_at: Optional[str] = File(None, description="Created At",example="2022-01-01 00:00:00")
    updated_at: Optional[str] = File(None, description="Updated At",example="2022-01-01 00:00:00")
    role: Optional[str] = File(None, description="Role",example="USER")
    status: Optional[str] = File(None, description="Status",example="ACTIVE")
    token: Optional[str] = File(None, description="Token",example="token")
    