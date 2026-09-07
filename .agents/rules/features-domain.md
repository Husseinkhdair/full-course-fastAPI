---
trigger: always_on
description: Rules and architectural blueprints for the Feature Domain layer (Entities, Abstract Repositories, and UseCases)
---

# Feature Domain Layer Architecture Rule (`Features/*/Domain/`)

## 1. Overview & Responsibility
The **Domain** layer represents the core business logic and rules of a Feature. It is strictly independent of databases, web frameworks (FastAPI), or ORMs. It consists of:
- **`Entities/`**: Pure domain data models with business identities and lifecycle logic.
- **`Repository/`**: Abstract interface contracts (ports) defining data operations.
- **`UseCases/`**: Encapsulated single-responsibility application workflows orchestrating domain logic.

**Folder Structure**:
```text
Features/<FeatureName>/Domain/
├── Entities/
│   └── <EntityName>Entity.py
├── Repository/
│   └── <FeatureName>Repository.py
└── UseCases/
    ├── __init__.py
    ├── Create<Entity>UseCase.py
    ├── Get<Entity>ByIdUseCase.py
    └── ...
```

---

## 2. Mandatory Architectural Rules

### 1) Pure Domain Entities (`Domain/Entities/`)
- Entities MUST NOT inherit from Pydantic `BaseModel` or SQLAlchemy `Base`. They are pure Python classes.
- Default fields must generate standard values:
  - `id`: Unique identifier (defaulting to `str(uuid.uuid4())`).
  - `created_at` / `updated_at`: UTC timestamp string `"%Y-%m-%d %H:%M:%S"`.
- Use Python standard library `Enum` classes for state/type values (e.g. `Role`, `Status`), referencing literal constants from `Core.Strings.*`.
- Implement `__str__` and `__repr__` for safe logging.

### 2) Abstract Repository Interface (`Domain/Repository/`)
- Must subclass `abc.ABC`.
- All methods MUST be decorated with `@abstractmethod` and defined as `async`.
- Method parameters must accept primitive Python types or Domain Entities.
- Method return types MUST be Domain Entities (e.g. `UserEntity`) or primitives (`bool`), NEVER ORM models or database dicts.

### 3) Single Responsibility UseCases (`Domain/UseCases/`)
- Each use case class encapsulates a single user interaction or business process (e.g. `CreateUserUseCase`, `LoginUserUseCase`).
- **Constructor Injection**:
  - `__init__(self, repository: <FeatureName>Repository)`
  - Must type-hint against the abstract repository interface, NOT concrete data sources.
- **Execution Method**:
  - Main workflow entry point is `async def execute(self, ...) -> <Entity>:`.
- **Exception Handling & Security**:
  - Catch domain exceptions (`AuthError`) and re-raise them directly.
  - Catch unexpected runtime errors, log with `logger.exception()`, and wrap in `ServerError(detail=str(e))`.
  - Perform security operations (such as JWT generation with `JWTPayload` from `Core.security.Jwt`) inside the use case or domain service.
- **Package Exports**:
  - `UseCases/__init__.py` MUST export all use case classes for clean importing across the project.

---

## 3. Code Blueprint & Reference Implementation

### `Features/Auth/Domain/Entities/UserEntity.py`
```python
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from Core.Strings.RoleString import admin, user, active, inactive, deleted

class Role(Enum):
    ADMIN = admin
    USER = user

class Status(Enum):
    ACTIVE = active
    INACTIVE = inactive
    DELETED = deleted

class UserEntity:
    def __init__(
        self,
        name: str,
        email: str,
        password: str,
        role: Role = Role.USER,
        status: Status = Status.ACTIVE,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        id: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.status = status

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = created_at if created_at is not None else now_str
        self.updated_at = updated_at if updated_at is not None else now_str
        self.id = id if id is not None else str(uuid.uuid4())
        self.token = token

    def __str__(self):
        role_str = self.role.value if isinstance(self.role, Role) else str(self.role)
        status_str = self.status.value if isinstance(self.status, Status) else str(self.status)
        return f"User(id={self.id}, name={self.name}, email={self.email}, role={role_str}, status={status_str})"

    def __repr__(self):
        return self.__str__()
```

### `Features/Auth/Domain/Repository/AuthRepository.py`
```python
from abc import ABC, abstractmethod
from Features.Auth.Domain.Entities.UserEntity import UserEntity

class AuthRepository(ABC):
    @abstractmethod
    async def create_user(self, email: str, name: str, password: str) -> UserEntity:
        pass

    @abstractmethod
    async def login_user(self, email: str, password: str) -> UserEntity:
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> UserEntity:
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserEntity:
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass
```

### `Features/Auth/Domain/UseCases/CreateUserUseCase.py`
```python
import logging
from Core.errors.AuthErrors import AuthError, UserAlredyExists, UserDoesNotExists
from Core.errors.GlobleErrors import ServerError
from Core.security.Jwt import JWTPayload, generate_token
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)

class CreateUserUseCase:
    def __init__(self, auth_repository: AuthRepository):
        self.auth_repository = auth_repository

    async def execute(self, email: str, name: str, password: str) -> UserEntity:
        try:
            try:
                is_user = await self.auth_repository.get_user_by_email(email)
                if is_user:
                    raise UserAlredyExists()
            except UserDoesNotExists:
                pass

            user = await self.auth_repository.create_user(email, name, password)

            role_str = user.role.value if hasattr(user.role, "value") else str(user.role)
            payload = JWTPayload(id=user.id, email=user.email, role=role_str)
            user.token = generate_token(payload)

            return user
        except AuthError:
            raise
        except Exception as e:
            logger.exception(f"error creating user: {email}")
            raise ServerError(detail=str(e))
```

---

## 4. Referenced In Master Architecture
- [Features Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-layer.md)
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
