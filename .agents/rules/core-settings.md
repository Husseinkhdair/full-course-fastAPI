---
trigger: always_on
description: Rules and guidelines for central settings and environment variable management in Core/Settings.py
---

# Core Settings Rule (`Core/Settings.py`)

## 1. Overview & Responsibility
The `Settings.py` module is the single source of truth for all runtime configuration and environment variables. It loads values from the `.env` file and encapsulates them in a strongly-typed, predictable container class.

**File Location**: `Core/Settings.py`

---

## 2. Mandatory Architectural Rules

1. **Module-Level `load_dotenv()`**:
   - `load_dotenv()` MUST be called at the very top of `Core/Settings.py` immediately after imports.
2. **Unified `SettingsApp` Class**:
   - All settings MUST be exposed as attributes of the `SettingsApp` class.
   - Type casting must be explicitly performed for non-string values (e.g., `access_token_expire_minutes` cast to `int`).
3. **No Direct `os.getenv` in Domain / Features / Repositories**:
   - Features, UseCases, Repositories, and Presentation controllers are **strictly forbidden** from calling `os.getenv()` or `load_dotenv()` directly.
   - Any component requiring configuration MUST instantiate or import `SettingsApp()`:
     ```python
     from Core.Settings import SettingsApp
     settings = SettingsApp()
     ```
4. **Default Values & Environment Safeguards**:
   - Sensitive keys (`secret_key`, `postgre_url`, `mongodb_url`) should be read directly from the environment.
   - Non-sensitive flags must provide safe defaults (e.g., `Development = os.getenv("Development", "True")`).

---

## 3. Code Blueprint & Reference Implementation

```python
import os
from dotenv import load_dotenv

# 1. Load environment variables at module initialization
load_dotenv()

class SettingsApp:
    def __init__(self):
        # Database Configurations
        self.mongodb_url: str = os.getenv("MONGODB_URL")
        self.mongodb_name: str = os.getenv("MONGODB_NAME")
        self.collection_users: str = os.getenv("COLLECTION_USERA", "users")
        self.postgre_url: str = os.getenv("PostgreURL")
        
        # Environment Mode
        self.Development: str = os.getenv("Development", "True")

        # Security & Token Configurations
        self.secret_key: str = os.getenv("SECRET_KEY")
        self.jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
```

---

## 4. Referenced In Master Architecture
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
