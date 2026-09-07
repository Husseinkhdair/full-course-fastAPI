---
trigger: always_on
description: Rules and guidelines for centralized Dependency Injection and repository/use-case wiring in Core/di.py
---

# Core Dependency Injection Rule (`Core/di.py`)

## 1. Overview & Responsibility
`di.py` is the central dependency injection composition root for FastAPI. It wires abstract domain interfaces to concrete data repositories and injects repositories into application UseCases.

**File Location**: `Core/di.py`

---

## 2. Mandatory Architectural Rules

1. **Composition Root Boundary**:
   - `di.py` is the **ONLY** file inside `Core/` permitted to import from `Features.*`.
   - Its sole purpose is wiring dependencies so that presentation routes remain completely agnostic of concrete data layers.
2. **Repository Providers**:
   - Provide explicit factory functions for each concrete repository implementation (e.g., `get_postgres_auth_repository()`, `get_mongodb_auth_repository()`).
   - Provide a primary switcher function (e.g., `get_auth_repository()`) that defaults to the active repository.
   - Return type hints MUST use the abstract Domain repository interface (`AuthRepository`), NOT concrete classes (`AuthRepositoryPostgresSQl`).
3. **UseCase Providers**:
   - Each UseCase MUST have its own provider function.
   - Inject the repository via FastAPI's `Depends(get_auth_repository)`.
   - Example:
     ```python
     def get_create_user_usecase(
         repo: AuthRepository = Depends(get_auth_repository)
     ) -> CreateUserUseCase:
         return CreateUserUseCase(repo)
     ```
4. **Usage in Presentation Routes**:
   - Endpoints in route files must NEVER instantiate use cases directly (e.g. `CreateUserUseCase(...)`).
   - Endpoints MUST inject use cases via `Depends(get_create_user_usecase)`.

---

## 3. Code Blueprint & Reference Implementation

```python
from fastapi import Depends
from fastapi.params import Depends as DependsParam

# Abstract Domain Repository & UseCases
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository
from Features.Auth.Domain.UseCases import (
    CreateUserUseCase,
    LoginUserUseCase,
    GetUserByIdUseCase,
    GetUserByEmailUseCase,
    DeleteUserUseCase
)

# Concrete Data Sources
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import AuthRepositoryPostgresSQl
from Features.Auth.Data.DataSources.AuthRepositoryMongoDB import AuthRepositoryMongoDB

# -----------------------------
# Repositories Dependency Providers
# -----------------------------
def get_postgres_auth_repository() -> AuthRepository:
    return AuthRepositoryPostgresSQl()

def get_mongodb_auth_repository() -> AuthRepository:
    return AuthRepositoryMongoDB()

def get_auth_repository(repo: AuthRepository = Depends(get_postgres_auth_repository)) -> AuthRepository:
    if isinstance(repo, DependsParam) or repo is None:
        return get_postgres_auth_repository()
    return repo

# -----------------------------
# UseCases Dependency Providers
# -----------------------------
def get_create_user_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> CreateUserUseCase:
    return CreateUserUseCase(repo)

def get_login_user_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> LoginUserUseCase:
    return LoginUserUseCase(repo)

def get_user_by_id_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> GetUserByIdUseCase:
    return GetUserByIdUseCase(repo)

def get_user_by_email_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> GetUserByEmailUseCase:
    return GetUserByEmailUseCase(repo)

def get_delete_user_usecase(
    repo: AuthRepository = Depends(get_auth_repository)
) -> DeleteUserUseCase:
    return DeleteUserUseCase(repo)
```

---

## 4. Referenced In Master Architecture
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
