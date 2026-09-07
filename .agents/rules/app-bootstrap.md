---
trigger: always_on
description: Architectural rules and lifecycle guidelines for FastAPI application bootstrap and entry point in main.py
---

# Application Bootstrap Rule (`main.py`)

## 1. Overview & Responsibility
`main.py` is the application's root entry point and runtime orchestrator. It bootstraps centralized logging, registers ASGI HTTP middleware, initializes application lifespans, and aggregates feature routers into the FastAPI application instance.

**File Location**: `main.py`

---

## 2. Mandatory Architectural Rules

1. **Strict Initialization Order**:
   Execution order during module import and startup MUST strictly follow this sequence:
   - **Step 1: Logging Setup**: Invoke `setup_logging()` from `Core.logging_config` *before* instantiating `FastAPI`.
   - **Step 2: Logger Resolution**: Obtain the root/module logger via `logger = logging.getLogger(__name__)`.
   - **Step 3: FastAPI Instantiation**: Create the `app = FastAPI(...)` instance.
   - **Step 4: HTTP Middleware Registration**: Register tracing and latency tracking middleware via `app.middleware("http")(middlewareApp)`.
   - **Step 5: Feature Router Mounting**: Mount feature routers via `app.include_router(...)`.
2. **Zero Inlined Business Logic**:
   - `main.py` must NEVER declare endpoints or inlined business logic routes directly. All routes belong to `Features/<FeatureName>/Presentation/route.py`.
   - `main.py` serves strictly as an assembly root.
3. **Dependency Injection Independence**:
   - `main.py` does not instantiate repositories or use cases directly; those are handled via `Core.di` and route dependency injection.
4. **Testability Contract**:
   - The `app` instance exported from `main.py` must be directly importable by test suites (`from main import app`) without triggering side-effect servers.

---

## 3. Code Blueprint & Reference Implementation

```python
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

# 1. Core Services & Middleware
from Core.logging_config import setup_logging
from Core.security.Middleware import middlewareApp

# 2. Feature Presentation Routers
from Features.Auth.Presentation.route import router as auth_router

# Step 1: Initialize structured JSON logging
setup_logging()
logger = logging.getLogger(__name__)

# Optional Lifespan Context Manager (if DB warmup/teardown is needed)
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up...")
    yield
    logger.info("Application shutting down...")

# Step 2: Create FastAPI application instance
app = FastAPI(
    title="FastAPI Clean Architecture",
    description="Scalable Clean Architecture backend",
    version="1.0.0",
    lifespan=lifespan
)

# Step 3: Register HTTP tracing and latency middleware
app.middleware("http")(middlewareApp)

# Step 4: Mount Feature routers
app.include_router(auth_router)
```

---

## 4. Referenced In Master Architecture
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
- [Features Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-layer.md)
- [Testing Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/testing-layer.md)
