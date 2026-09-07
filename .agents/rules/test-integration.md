---
trigger: always_on
description: Rules and implementation guidelines for Integration Testing in Tests/Integration/
---

# Integration Testing Architecture Rule (`Tests/Integration/`)

## 1. Overview & Responsibility
Integration tests verify the collaboration between interconnected components, including real database sessions, repositories, use cases, and HTTP routers. They ensure database queries, transaction rollbacks, and schema conversions execute correctly against active storage systems.

**Folder Structure**:
```text
Tests/Integration/<FeatureName>/
├── DataSoruces/              # Real SQL & NoSQL repository operations
│   ├── test_<feature>_repository_postgres_sql.py
│   └── test_<feature>_repository_mongos_db.py
├── UseCases/                 # Use cases orchestrating real repositories
│   ├── test_create_<entity>_use_case.py
│   └── ...
└── Presentation/             # Full HTTP flow testing without mocks
    └── test_<feature>_presentation_integration.py
```

---

## 2. Mandatory Architectural Rules

1. **Pytest Integration Marker**:
   - Every integration test file or function MUST be decorated with `@pytest.mark.integration`.
2. **Asynchronous Execution**:
   - Tests exercising async repository methods or use cases MUST be declared with `async def test_*(...)`.
   - `pytest.ini` with `asyncio_mode = auto` automatically handles event loop lifecycles.
3. **Database Schema & Table Fixtures**:
   - Postgres tests must ensure tables are initialized using fixtures:
     ```python
     @pytest.fixture
     def auth_repository():
         Base.metadata.create_all(bind=engine)
         return AuthRepositoryPostgresSQl()
     ```
4. **Mandatory Test Teardown & Data Cleanup**:
   - Integration tests insert real database records.
   - **MANDATORY**: Every test must delete or roll back any persisted entity it created to ensure test idempotency and prevent duplicate key violations:
     ```python
     user = await auth_repository.create_user(...)
     try:
         # Assertions...
     finally:
         await auth_repository.delete_user(user.id)
     ```
5. **Expected Domain Exception Assertions**:
   - Verify that domain exceptions are accurately raised using `pytest.raises`:
     ```python
     with pytest.raises(UserDoesNotExists):
         await auth_repository.get_user_by_id("non_existent_id")
     ```

---

## 3. Code Blueprint & Reference Implementation

### `Tests/Integration/Auth/DataSoruces/test_auth_repository_postgres_sql.py`
```python
import pytest
from Core.DataBase.PostgresDB import engine
from Core.errors.AuthErrors import UserDoesNotExists, UserAlredyExists
from Features.Auth.Data.DataSources.AuthRepositoryPostegresSQL import AuthRepositoryPostgresSQl
from Features.Auth.Data.Models.AuthModelPostgres import Base
from Features.Auth.Domain.Entities.UserEntity import UserEntity

@pytest.fixture
def auth_repository():
    Base.metadata.create_all(bind=engine)
    return AuthRepositoryPostgresSQl()

@pytest.mark.integration
async def test_create_and_delete_user_postgres(auth_repository: AuthRepositoryPostgresSQl):
    email = "pg_integration@test.com"
    user = await auth_repository.create_user(email, "Pg User", "password123")
    
    assert user is not None
    assert isinstance(user, UserEntity)
    assert user.email == email

    # Teardown / Cleanup
    deleted = await auth_repository.delete_user(user.id)
    assert deleted is True

    # Confirm deletion
    with pytest.raises(UserDoesNotExists):
        await auth_repository.get_user_by_id(user.id)
```

---

## 4. Referenced In Master Architecture
- [Testing Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/testing-layer.md)
- [Features Data Rule](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-data.md)
