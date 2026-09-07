---
trigger: always_on
description: Rules and guidelines for database engines, connection lifecycles, and session pooling in Core/DataBase/
---

# Core Database Management Rule (`Core/DataBase/`)

## 1. Overview & Responsibility
The `Core/DataBase/` subpackage handles database connection clients, session lifecycle factories, and dynamic proxies for both Relational (SQLAlchemy) and NoSQL (PyMongo Async) databases.

**Folder Location**: `Core/DataBase/`
- `PostgresDB.py` (SQLAlchemy Relational Engine)
- `MongoDb.py` (PyMongo Async Document Store)

---

## 2. Mandatory Architectural Rules

### 1) Relational DB: `PostgresDB.py`
- Must import configuration through `from Core.Settings import SettingsApp`.
- Create the SQLAlchemy engine via `create_engine(settings.postgre_url)`.
- Expose a `SessionLocal` factory with `autoflush=False` and `autocommit=False`.

### 2) NoSQL DB: `MongoDb.py`
- Use `AsyncMongoClient` from `pymongo`.
- **Async Event-Loop Safe Client Caching**:
  - Python async runtimes (FastAPI, pytest-asyncio, AnyIO) can change event loops across tests or requests.
  - Maintain a module-level cache `_clients = {}`.
  - In `get_mongo_client()`, resolve `loop = asyncio.get_running_loop()`. If `loop not in _clients`, create a new `AsyncMongoClient(MONGODB_URL)`.
- **Dynamic Collection Proxy (`CollectionProxy`)**:
  - To prevent binding collection names statically at import time before settings are loaded or during tests, wrap collections with `CollectionProxy(lambda: settings.collection_users)`.

---

## 3. Code Blueprint & Reference Implementation

### `Core/DataBase/PostgresDB.py`
```python
from Core.Settings import SettingsApp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = SettingsApp()
engine = create_engine(settings.postgre_url)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)
```

### `Core/DataBase/MongoDb.py`
```python
import asyncio
from pymongo import AsyncMongoClient
from Core.Settings import SettingsApp

settings = SettingsApp()
MONGODB_URL = settings.mongodb_url
MONGODB_NAME = settings.mongodb_name

_clients = {}

def get_mongo_client() -> AsyncMongoClient:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop not in _clients or _clients[loop] is None:
        _clients[loop] = AsyncMongoClient(MONGODB_URL)
    return _clients[loop]

def get_db():
    return get_mongo_client()[MONGODB_NAME]

class CollectionProxy:
    def __init__(self, get_name):
        self.get_name = get_name

    def __getattr__(self, name):
        coll = get_db()[self.get_name()]
        return getattr(coll, name)

collection_users = CollectionProxy(lambda: settings.collection_users)
```

---

## 4. Referenced In Master Architecture
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
