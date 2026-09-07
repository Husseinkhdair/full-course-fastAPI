---
trigger: always_on
description: Rules and guidelines for domain and HTTP exception hierarchy in Core/errors/
---

# Core Error Handling & Exceptions Rule (`Core/errors/`)

## 1. Overview & Responsibility
The `Core/errors/` subpackage defines a clean, strongly-typed domain exception hierarchy extending `fastapi.HTTPException`. It prevents unhandled raw exceptions from leaking to API clients and standardizes status codes across the application.

**Folder Location**: `Core/errors/`
- `GlobleErrors.py` (General & infrastructure errors, 500)
- `AuthErrors.py` (Authentication & authorization errors, 400/401/403)

---

## 2. Mandatory Architectural Rules

1. **Subclassing `fastapi.HTTPException`**:
   - All domain errors MUST subclass `HTTPException` so that FastAPI can serialize them automatically into JSON responses with proper HTTP status codes.
2. **Domain Grouping**:
   - Base domain class `GlobleErrors(HTTPException)` handles system-level errors.
   - Base domain class `AuthError(HTTPException)` handles authentication/access errors.
3. **Production Detail Masking**:
   - For `ServerError` (HTTP 500), check `SettingsApp().Development`.
   - If `Development == "False"`, internal tracebacks or exception messages MUST be replaced with a generic `"Server error"` to prevent information disclosure vulnerabilities.
4. **Standard Status Codes in `AuthErrors`**:
   - `UserAlredyExists`: HTTP 400 (`"User alredy exists"`)
   - `UserDoesNotExists`: HTTP 400 (`"User does not exists"`)
   - `InvalidEmailOrPassword`: HTTP 401 (`"Invalid email or password"`)
   - `UserNotHaveRole`: HTTP 403 (`"User not have role"`)
   - `InvalidToken`: HTTP 401 (`"Invalid token"`)

---

## 3. Code Blueprint & Reference Implementation

### `Core/errors/GlobleErrors.py`
```python
from fastapi import HTTPException
from Core.Settings import SettingsApp

class GlobleErrors(HTTPException):
    def __init__(self, detail: str, status_code: int):
        super().__init__(status_code, detail)

class ServerError(GlobleErrors):
    def __init__(self, detail: str = "Server error"):
        if SettingsApp().Development == "False":
            detail = "Server error"
        super().__init__(detail, 500)
```

### `Core/errors/AuthErrors.py`
```python
from fastapi import HTTPException

class AuthError(HTTPException):
    def __init__(self, detail: str, status_code: int):
        super().__init__(status_code, detail)

class UserAlredyExists(AuthError):
    def __init__(self):
        super().__init__("User alredy exists", 400)

class UserDoesNotExists(AuthError):
    def __init__(self):
        super().__init__("User does not exists", 400)

class InvalidEmailOrPassword(AuthError):
    def __init__(self):
        super().__init__("Invalid email or password", 401)

class UserNotHaveRole(AuthError):
    def __init__(self):
        super().__init__("User not have role", 403)

class InvalidToken(AuthError):
    def __init__(self):
        super().__init__("Invalid token", 401)
```

---

## 4. Referenced In Master Architecture
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
