---
trigger: always_on
description: Rules and implementation guidelines for End-to-End (E2E) testing in Tests/E2E/
---

# End-to-End (E2E) Testing Architecture Rule (`Tests/E2E/`)

## 1. Overview & Responsibility
End-to-End (E2E) tests validate complete vertical user journeys from HTTP request ingestion through middleware, routers, use cases, databases, and response delivery. They simulate realistic client consumption and verify multi-step business transactions.

**Folder Structure**:
```text
Tests/E2E/
└── test_<feature>_e2e.py     # Complete multi-step user lifecycle & isolation flows
```

---

## 2. Mandatory Architectural Rules

1. **Pytest E2E Marker**:
   - All E2E test functions and test files MUST be decorated with `@pytest.mark.e2e`.
2. **Client Fixture**:
   - Use `TestClient(app)` from `fastapi.testclient` importing the real `app` instance from `main`.
3. **Complete Lifecycle Journey**:
   - An E2E test must cover an unbroken sequence of operations:
     1. Account registration (`POST /<feature>/register`).
     2. Cryptographic token verification (`verify_token(token)` from `Core.security.Jwt`).
     3. Authentication / Login (`POST /<feature>/login`).
     4. Resource retrieval by identifiers (`GET /<feature>/...`).
     5. Resource deletion / cleanup (`DELETE /<feature>/...`).
     6. Post-deletion validation (ensuring subsequent login or retrieval requests fail).
4. **Data Isolation Across Users**:
   - Include tests validating that multiple concurrently created users cannot read or mutate each other's data.
5. **Schema Validation & Error Cases**:
   - Verify HTTP 422 Unprocessable Entity for invalid email formats and password constraint violations (e.g. min_length).
6. **Teardown & Cleanup Guarantees**:
   - Always delete created accounts at the end of each test scenario to leave the database clean.

---

## 3. Code Blueprint & Reference Implementation

### `Tests/E2E/test_auth_e2e.py` (Excerpt)
```python
import pytest
from fastapi.testclient import TestClient
from main import app
from Core.security.Jwt import verify_token

@pytest.fixture
def e2e_client():
    return TestClient(app)

@pytest.mark.e2e
def test_e2e_complete_user_lifecycle(e2e_client: TestClient):
    email = "e2e_sample_lifecycle@example.com"
    name = "E2E User"
    password = "password123"

    # 1. Register User
    reg_res = e2e_client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password}
    )
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    user_id = str(reg_data["user_id"])
    token = reg_data["token"]

    # 2. Verify Generated JWT
    payload = verify_token(token)
    assert payload is not None
    assert payload.id == user_id

    # 3. Login
    login_res = e2e_client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    assert login_res.status_code == 200

    # 4. Fetch Profile
    get_res = e2e_client.get(f"/auth/user/id/{user_id}")
    assert get_res.status_code == 200
    assert get_res.json()["email"] == email

    # 5. Delete Account
    del_res = e2e_client.delete(f"/auth/user/id/{user_id}")
    assert del_res.status_code == 200

    # 6. Verify Login Fails After Account Deletion
    post_del_login = e2e_client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    assert post_del_login.status_code in (400, 401, 500)
```

---

## 4. Referenced In Master Architecture
- [Testing Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/testing-layer.md)
- [Application Bootstrap Rule](file:///c:/Users/dell-four/Desktop/test/.agents/rules/app-bootstrap.md)
