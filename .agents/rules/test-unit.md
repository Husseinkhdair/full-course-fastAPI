---
trigger: always_on
description: Rules and implementation guidelines for isolated Unit Testing in Tests/Unit/
---

# Unit Testing Architecture Rule (`Tests/Unit/`)

## 1. Overview & Responsibility
Unit tests verify individual functions, entities, mappers, and route controllers in total isolation from network I/O and external databases. They execute rapidly in-memory using mocks and dependency overrides.

**Folder Structure**:
```text
Tests/Unit/
├── <FeatureName>/
│   ├── test_<feature>_models.py   # Entity & database model bidirectional mappers
│   └── test_<feature>_routes.py   # Route handlers with mocked UseCases
└── Core/
    ├── DataBase/                  # Connection helper & proxy tests
    ├── security/                  # Password hashing & JWT lifecycle tests
    ├── test_di.py                 # Dependency Injection resolution tests
    └── test_settings.py           # Configuration loading tests
```

---

## 2. Mandatory Architectural Rules

### 1) Route Controller Unit Tests (`test_<feature>_routes.py`)
- **FastAPI `TestClient`**:
  - Instantiate via pytest fixture `@pytest.fixture def client(): return TestClient(app)`.
- **UseCase Mocking**:
  - Use `unittest.mock.AsyncMock` for async UseCases.
  - Configure return values with domain entities:
    ```python
    mock_usecase = AsyncMock()
    mock_usecase.execute.return_value = mock_user_entity
    ```
- **Dependency Overrides**:
  - Override specific DI providers in `app.dependency_overrides`:
    ```python
    app.dependency_overrides[get_create_user_usecase] = lambda: mock_usecase
    ```
- **State Isolation Cleanup**:
  - **MANDATORY**: Every test using overrides must call `app.dependency_overrides.clear()` at completion (or in a teardown fixture) to prevent test contamination.
- **Assertion Standards**:
  - Assert HTTP status code (`assert response.status_code == 201`).
  - Assert serialized response payload matches expected schema fields.

### 2) Model & Mapper Unit Tests (`test_<feature>_models.py`)
- Test default attribute initialization.
- Test custom attribute initialization.
- Validate bidirectional transformations:
  - `model.to_entity()` produces a valid Domain Entity.
  - `Model.from_entity(entity)` produces a valid ORM/Document model.
  - `model.to_dict()` and `Model.from_dict(dict)` for document stores.

### 3) Core Security & Utility Tests (`Tests/Unit/Core/`)
- Test `hash_password()` and `verify_password()` with valid and invalid credentials.
- Test `generate_token()` and `verify_token()` with valid payloads, expired tokens, and malformed strings.

---

## 3. Code Blueprint & Reference Implementation

### `Tests/Unit/Auth/test_auth_routes.py`
```python
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from main import app
from Core.di import get_create_user_usecase
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status

@pytest.fixture
def client():
    return TestClient(app)

def test_register_user_route(client):
    mock_usecase = AsyncMock()
    mock_user = UserEntity(
        id="user_123",
        name="Hussein",
        email="hussein@gmail.com",
        password="hashed_pwd",
        role=Role.USER,
        status=Status.ACTIVE,
    )
    mock_user.token = "sample_jwt_token"
    mock_usecase.execute.return_value = mock_user

    app.dependency_overrides[get_create_user_usecase] = lambda: mock_usecase

    response = client.post(
        "/auth/register",
        json={"name": "Hussein", "email": "hussein@gmail.com", "password": "password123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "hussein@gmail.com"
    assert data["name"] == "Hussein"
    assert data["token"] == "sample_jwt_token"

    app.dependency_overrides.clear()
```

---

## 4. Referenced In Master Architecture
- [Testing Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/testing-layer.md)
- [Application Bootstrap Rule](file:///c:/Users/dell-four/Desktop/test/.agents/rules/app-bootstrap.md)
