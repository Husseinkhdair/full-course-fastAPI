---
trigger: always_on
description: Rules and guidelines for password hashing, JWT authentication, and ASGI HTTP tracing middleware in Core/security/
---

# Core Security, Cryptography & Middleware Rule (`Core/security/`)

## 1. Overview & Responsibility
The `Core/security/` subpackage secures the application through cryptographic password hashing (`Password.py`), strongly-typed JWT authentication (`Jwt.py`), and ASGI HTTP request tracking middleware (`Middleware.py`).

**Folder Location**: `Core/security/`
- `Password.py`
- `Jwt.py`
- `Middleware.py`

---

## 2. Mandatory Architectural Rules

### 1) Password Hashing (`Password.py`)
- **Strictly use `bcrypt`** (never MD5, SHA256, or deprecated `passlib`).
- Implement `PasswordSecurity` with static methods:
  - `hash_password(password: str) -> str`: Generates salt with `bcrypt.gensalt()`, encodes UTF-8, decodes back to `str`.
  - `verify_password(plain_password: str, hashed_password: str) -> bool`: Safe verification catching all exceptions and returning `False` on malformed hashes.
- Expose module-level helper aliases: `hash_password()` and `verify_password()`.

### 2) JWT Token Lifecycle (`Jwt.py`)
- Define an explicit data class/model `JWTPayload` with attributes `(id, email, role, exp)` and serialization methods `to_dict()` and `@classmethod from_dict(cls, data)`.
- **`generate_token(payload, secret_key, algorithm, expires_delta)`**:
  - Expiration timestamp MUST be computed in UTC: `datetime.now(timezone.utc) + delta`.
  - Fall back to `SettingsApp` attributes (`secret_key`, `jwt_algorithm`, `access_token_expire_minutes`) if parameters are omitted.
  - On any encoding error or exception, log error and raise `InvalidToken()`.
- **`verify_token(token, secret_key, algorithm)`**:
  - Decodes with `jwt.decode(token, key, algorithms=[algo])`.
  - Returns reconstructed `JWTPayload` or catches exceptions and raises `InvalidToken()`.

### 3) HTTP Tracing Middleware (`Middleware.py`)
- Async middleware function `middlewareApp(request: Request, call_next)`.
- Extract `X-Request-ID` header, or generate a new `str(uuid.uuid4())` if missing.
- Set context token: `request_id_token = request_id_var.set(request_id)`.
- Measure latency in milliseconds: `duration = round((time.time() - start_time) * 1000, 2)`.
- Inject `X-Request-ID` into response headers: `response.headers["X-Request-ID"] = request_id`.
- Log request initiation and completion with `path`, `method`, `status_code`, and `duration`.
- **Crucial**: ALWAYS reset the context variable in `finally: request_id_var.reset(request_id_token)`.

---

## 3. Code Blueprint & Reference Implementation

### `Core/security/Password.py`
```python
import bcrypt

class PasswordSecurity:
    @staticmethod
    def hash_password(password: str) -> str:
        if not password:
            raise ValueError("Password cannot be empty")
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        if not plain_password or not hashed_password:
            return False
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8")
            )
        except Exception:
            return False

def hash_password(password: str) -> str:
    return PasswordSecurity.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return PasswordSecurity.verify_password(plain_password, hashed_password)
```

### `Core/security/Jwt.py`
```python
from Core.errors.AuthErrors import InvalidToken
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
import logging
from Core.Settings import SettingsApp

settings = SettingsApp()
logger = logging.getLogger(__name__)

class JWTPayload:
    def __init__(
        self,
        id: str,
        email: Optional[str] = None,
        role: Optional[str] = None,
        exp: Optional[int] = None
    ):
        self.id = id
        self.email = email
        self.role = role
        self.exp = exp

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {"id": str(self.id)}
        if self.email is not None:
            data["email"] = self.email
        if self.role is not None:
            data["role"] = str(self.role)
        if self.exp is not None:
            data["exp"] = self.exp
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JWTPayload":
        if not data:
            return None
        data_copy = dict(data)
        return cls(
            id=str(data_copy.pop("id", "")),
            email=data_copy.pop("email", None),
            role=data_copy.pop("role", None),
            exp=data_copy.pop("exp", None)
        )

def generate_token(
    payload: JWTPayload,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    try:
        key = secret_key or settings.secret_key
        algo = algorithm or settings.jwt_algorithm
        payload_dict = payload.to_dict()

        now = datetime.now(timezone.utc)
        if "exp" not in payload_dict or payload_dict["exp"] is None:
            delta = expires_delta if expires_delta is not None else timedelta(minutes=settings.access_token_expire_minutes)
            payload_dict["exp"] = int((now + delta).timestamp())

        logger.debug("Token created successfully")
        return jwt.encode(payload_dict, key, algorithm=algo)
    except Exception as e:
        logger.exception(f"Error creating token: {e}")
        raise InvalidToken()

def verify_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> Optional[JWTPayload]:
    key = secret_key or settings.secret_key
    algo = algorithm or settings.jwt_algorithm
    try:
        decoded = jwt.decode(token, key, algorithms=[algo])
        logger.debug("Token verified successfully")
        return JWTPayload.from_dict(decoded)
    except Exception as e:
        logger.debug(f"Invalid token: {e}")
        raise InvalidToken()
```

### `Core/security/Middleware.py`
```python
import time
import uuid
import logging
from fastapi import Request
from Core.logging_config import request_id_var

logger = logging.getLogger('Middleware.py')

async def middlewareApp(request: Request, call_next):
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request_id_token = request_id_var.set(request_id)

    path = request.url.path
    method = request.method

    try:
        logger.info("Request Received", extra={"path": path, "method": method})
        response = await call_next(request)
        duration = round((time.time() - start_time) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        
        logger.info("Request Completed", extra={
            "path": path,
            "method": method,
            "status_code": response.status_code,
            "duration": f"{duration}ms"
        })
        return response
    except Exception as e:
        duration = round((time.time() - start_time) * 1000, 2)
        logger.error("Request Failed", extra={
            "path": path,
            "method": method,
            "duration": f"{duration}ms",
            "error": str(e)
        })
        raise e
    finally:
        request_id_var.reset(request_id_token)
```

---

## 4. Referenced In Master Architecture
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
