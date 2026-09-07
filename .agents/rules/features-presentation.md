---
trigger: always_on
description: Rules and architectural blueprints for the Feature Presentation layer (Pydantic DTOs and FastAPI Route Controllers)
---

# Feature Presentation Layer Architecture Rule (`Features/*/Presentation/`)

## 1. Overview & Responsibility
The **Presentation** layer handles the HTTP interface, input validation, request parsing, and response serialization for FastAPI. It connects external API clients to application UseCases while remaining strictly decoupled from data persistence details.

**Folder Structure**:
```text
Features/<FeatureName>/Presentation/
├── route.py                  # FastAPI APIRouter and route handlers
└── tdo.py                    # Pydantic DTOs (Data Transfer Objects / Schemas)
```

---

## 2. Mandatory Architectural Rules

### 1) Data Transfer Objects / Schemas (`tdo.py`)
- Define distinct request and response schemas subclassing `pydantic.BaseModel`.
- **Request Schemas**:
  - Enforce field validation using `Field(...)`, constraints (`min_length`, `max_length`), and typed fields (e.g. `EmailStr`).
  - Provide OpenAPI documentation examples via `json_schema_extra={"example": ...}`.
- **Response Schemas**:
  - Model attributes must match API output contracts.
  - MUST implement a factory method `@classmethod from_entity(cls, entity: <Entity>Entity) -> <SchemaTDO>` to serialize pure domain entities into response models.
  - Safely resolve Enum values to their string representations (`entity.role.value if hasattr(entity.role, "value") else str(entity.role)`).

### 2) Route Controllers (`route.py`)
- Instantiate an `APIRouter` with an explicit URL prefix and documentation tags:
  ```python
  router = APIRouter(prefix="/<feature>", tags=["<Feature>"])
  ```
- **Zero Direct Instantiation**:
  - Route handlers must NEVER instantiate use cases directly (e.g. `CreateUserUseCase(...)`).
  - Route handlers must NEVER access database sessions or repositories directly.
- **Dependency Injection**:
  - Inject use cases exclusively via FastAPI's `Depends` importing providers from `Core.di`:
    ```python
    @router.post("/register", response_model=InfoUserTDO, status_code=status.HTTP_201_CREATED)
    async def register_user(
        user: CreateUserTDO,
        usecase: CreateUserUseCase = Depends(get_create_user_usecase)
    ):
        user_entity = await usecase.execute(email=user.email, name=user.name, password=user.password)
        return InfoUserTDO.from_entity(user_entity)
    ```
- **Explicit HTTP Contracts**:
  - Always declare `response_model` on endpoints.
  - Always declare appropriate `status_code` (e.g., `status.HTTP_201_CREATED` for creation, `status.HTTP_200_OK` for retrievals).

---

## 3. Code Blueprint & Reference Implementation

### `Features/Auth/Presentation/tdo.py`
```python
from typing import Optional, Union
from pydantic import BaseModel, EmailStr, Field
from Features.Auth.Domain.Entities.UserEntity import UserEntity

class CreateUserTDO(BaseModel):
    name: str = Field(..., description="Name", json_schema_extra={"example": "Hussein"}, min_length=1, max_length=255)
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    password: str = Field(..., description="Password", json_schema_extra={"example": "password123"}, min_length=6, max_length=16)

class LoginTDO(BaseModel):
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    password: str = Field(..., description="Password", json_schema_extra={"example": "password123"}, min_length=6, max_length=16)

class InfoUserTDO(BaseModel):
    user_id: Union[str, int] = Field(..., description="User ID", json_schema_extra={"example": "123"})
    email: EmailStr = Field(..., description="Email", json_schema_extra={"example": "hussein@gmail.com"})
    name: str = Field(..., description="Name", json_schema_extra={"example": "Hussein"})
    created_at: Optional[str] = Field(None, description="Created At")
    updated_at: Optional[str] = Field(None, description="Updated At")
    role: Optional[str] = Field(None, description="Role")
    status: Optional[str] = Field(None, description="Status")
    token: Optional[str] = Field(None, description="Token")

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
```

### `Features/Auth/Presentation/route.py`
```python
from fastapi import APIRouter, Depends, status
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    DeleteUserUseCase
)
from Features.Auth.Presentation.tdo import CreateUserTDO, LoginTDO, InfoUserTDO
from Core.di import (
    get_create_user_usecase,
    get_login_user_usecase,
    get_user_by_id_usecase,
    get_delete_user_usecase
)

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=InfoUserTDO, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: CreateUserTDO,
    usecase: CreateUserUseCase = Depends(get_create_user_usecase)
):
    user_entity = await usecase.execute(email=user.email, name=user.name, password=user.password)
    return InfoUserTDO.from_entity(user_entity)

@router.post("/login", response_model=InfoUserTDO, status_code=status.HTTP_200_OK)
async def login_user(
    user: LoginTDO,
    usecase: LoginUserUseCase = Depends(get_login_user_usecase)
):
    user_entity = await usecase.execute(email=user.email, password=user.password)
    return InfoUserTDO.from_entity(user_entity)
```

---

## 4. Referenced In Master Architecture
- [Features Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-layer.md)
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
