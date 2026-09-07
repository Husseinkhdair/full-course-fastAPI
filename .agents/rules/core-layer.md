---
trigger: always_on
description: Master architectural blueprint, directory layout, and component index for the Core layer in FastAPI clean architecture projects.
---

# Core Layer Master Architecture Blueprint

The **Core** layer is the central architectural backbone of the application. It encapsulates cross-cutting concerns, infrastructure services, and shared utilities consumed by feature and presentation layers, following the principles of **Clean Architecture** and **Domain-Driven Design (DDD)**.

---

## 1. Directory Structure

Any FastAPI project adhering to this architecture MUST follow this exact directory structure under `Core/`:

```text
Core/
│
├── Settings.py               # Central environment and configuration management
├── logging_config.py         # Structured JSON logging & context variables (tracing)
├── di.py                     # Dependency Injection providers (FastAPI Depends)
│
├── DataBase/                 # Database clients and connection lifecycles
│   ├── PostgresDB.py         # SQLAlchemy relational database engine & sessionmaker
│   └── MongoDb.py            # PyMongo async client, DB getters, and CollectionProxy
│
├── security/                 # Security, cryptography, tokens, and middleware
│   ├── Jwt.py                # JWT payload models, token generation, and validation
│   ├── Password.py           # Bcrypt password hashing and verification
│   └── Middleware.py         # ASGI HTTP Middleware for Request-ID tracing & timing
│
├── errors/                   # Unified domain & HTTP exception hierarchy
│   ├── GlobleErrors.py       # General server errors (500) and environment safeguards
│   └── AuthErrors.py         # Semantic authentication & authorization exceptions
│
└── Strings/                  # Constant string literals to eliminate magic strings
    └── RoleString.py         # Role names and entity statuses
```

---

## 2. Specialized Rules & Component Map

The detailed rules, code blueprints, and implementation specifications for each Core component are partitioned into dedicated rule files. Consult and adhere to each specialized rule file below:

| Component | Target File(s) in Codebase | Dedicated Rule File | Rule Path |
| :--- | :--- | :--- | :--- |
| **Settings & Config** | `Core/Settings.py` | [core-settings.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-settings.md) | `.agents/rules/core-settings.md` |
| **Structured Logging** | `Core/logging_config.py` | [core-logging.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-logging.md) | `.agents/rules/core-logging.md` |
| **Databases (SQL & NoSQL)** | `Core/DataBase/*` | [core-database.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-database.md) | `.agents/rules/core-database.md` |
| **Dependency Injection** | `Core/di.py` | [core-di.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-di.md) | `.agents/rules/core-di.md` |
| **Security & Middleware** | `Core/security/*` | [core-security.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-security.md) | `.agents/rules/core-security.md` |
| **Error Handling** | `Core/errors/*` | [core-errors.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-errors.md) | `.agents/rules/core-errors.md` |
| **String Literals** | `Core/Strings/*` | [core-strings.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-strings.md) | `.agents/rules/core-strings.md` |

---

## 3. Foundational Architectural Principles

1. **Inversion of Control & Clean Layer Boundaries**:
   - The `Core/` layer must NEVER import business logic, models, or schemas from `Features/`.
   - The **ONLY** exception is `Core/di.py`, which serves as the composition root to wire abstract domain interfaces to concrete repositories and use cases.
2. **Single Source of Configuration**:
   - All modules, features, and database layers must read configuration strictly through `SettingsApp()` from `Core.Settings`. Calling `os.getenv()` directly is prohibited.
3. **Structured Contextual Tracing**:
   - All HTTP requests are assigned a unique `X-Request-ID` via ASGI middleware in `Core/security/Middleware.py`, recorded in `request_id_var` and propagated through `Core/logging_config.py`.
4. **Standardized Domain Exceptions**:
   - Never allow unhandled Python runtime exceptions to reach the client. Group exceptions under `Core/errors/` inheriting from `fastapi.HTTPException`.
5. **Decoupled Presentation via Dependency Injection**:
   - Endpoints in route files must never instantiate repositories or use cases directly. They must inject them using `Depends()` defined in `Core/di.py`.

---

## 4. Application Bootstrap in `main.py`

Whenever initializing a FastAPI application that adheres to this Core layer:
1. Always call `setup_logging()` before creating or running the app.
2. Register `middlewareApp` on the FastAPI instance.
3. Include feature routers.

```python
import logging
from fastapi import FastAPI
from Core.logging_config import setup_logging
from Core.security.Middleware import middlewareApp
from Features.Auth.Presentation.route import router as auth_router

# 1. Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# 2. Create FastAPI instance
app = FastAPI()

# 3. Register HTTP tracing middleware
app.middleware("http")(middlewareApp)

# 4. Include feature routers
app.include_router(auth_router)
```

---

## 5. Cross-Layer Architecture Reference
- [Features Master Architecture Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-layer.md)
- [Testing Master Architecture Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/testing-layer.md)
- [Application Bootstrap Rule](file:///c:/Users/dell-four/Desktop/test/.agents/rules/app-bootstrap.md)


