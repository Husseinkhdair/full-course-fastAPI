---
trigger: always_on
description: Rules and architectural blueprints for the Feature Data layer (ORM/Document Models and Concrete DataSources)
---

# Feature Data Layer Architecture Rule (`Features/*/Data/`)

## 1. Overview & Responsibility
The **Data** layer implements data persistence, database querying, and external storage communication for a Feature. It implements the abstract ports defined by the Domain layer and handles translation between database records and pure Domain Entities.

**Folder Structure**:
```text
Features/<FeatureName>/Data/
├── Models/
│   ├── <FeatureName>ModelPostgres.py  # SQLAlchemy ORM model & entity mappers
│   └── <FeatureName>ModelMongos.py    # Mongo document schema & entity mappers
└── DataSources/
    ├── <FeatureName>RepositoryPostgresSQL.py # Relational data repository
    └── <FeatureName>RepositoryMongoDB.py     # NoSQL async document repository
```

---

## 2. Mandatory Architectural Rules

### 1) Data Persistence Models (`Data/Models/`)
- Every data model MUST provide explicit conversion methods to decouple the database representation from the domain:
  - `to_entity(self) -> <Entity>Entity`: Converts database instance into a pure domain entity.
  - `@classmethod from_entity(cls, entity: <Entity>Entity)`: Constructs a model instance from a domain entity.
- **SQLAlchemy Relational Models (`ModelPostgres.py`)**:
  - Subclass `DeclarativeBase`.
  - Column annotations MUST use `Mapped[...] = mapped_column(...)`.
  - Read table names dynamically from `SettingsApp().<collection_or_table_name>`.
- **NoSQL Mongo Document Models (`ModelMongos.py`)**:
  - Implement serialization: `to_dict() -> Dict[str, Any]` (mapping `id` to `_id`).
  - Implement deserialization: `@classmethod from_dict(cls, data: Dict[str, Any])` (resolving `_id` / `id`).

### 2) Concrete Data Sources (`Data/DataSources/`)
- Must subclass the abstract domain repository interface (`AuthRepository`).
- **Relational Data Source (`PostgresSQL`)**:
  - Inject database session via `__init__(self, db=None)` defaulting to `SessionLocal()` from `Core.DataBase.PostgresDB`.
  - Explicit transaction boundaries:
    - Call `self.db.commit()` on successful mutations.
    - Always invoke `self.db.rollback()` in `except` blocks before re-raising or wrapping errors.
  - Query using SQLAlchemy 2.0 style syntax: `self.db.execute(select(Model).where(...)).scalars().first()`.
- **NoSQL Data Source (`MongoDB`)**:
  - Import the dynamic collection proxy from `Core.DataBase.MongoDb` (e.g. `collection_users`).
  - Support flexible ID lookups: query against both `id` and `_id`, and convert to `ObjectId` if valid.
  - Execute async operations: `await self.collection.find_one(...)`, `await self.collection.insert_one(...)`.
- **Security & Exceptions**:
  - Never store plain passwords; always hash using `hash_password(password)` from `Core.security.Password`.
  - Compare credentials with `verify_password(password, stored_hash)`.
  - Raise specific domain exceptions (`UserAlredyExists`, `UserDoesNotExists`, `InvalidEmailOrPassword`) from `Core.errors.AuthErrors`.
  - Catch unexpected infrastructure errors, log with `logger.exception()`, and wrap in `ServerError(detail=str(e))`.

---

## 3. Code Blueprint & Reference Implementation

### `Features/Auth/Data/Models/AuthModelPostgres.py`
```python
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from Core.Settings import SettingsApp
from Features.Auth.Domain.Entities.UserEntity import UserEntity, Role, Status

settings = SettingsApp()

class Base(DeclarativeBase):
    pass

class AuthPostgresModel(Base):
    __tablename__ = settings.collection_users

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=Role.USER.value)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default=Status.ACTIVE.value)
    created_at: Mapped[str] = mapped_column(String(100), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(100), nullable=False)

    def to_entity(self) -> UserEntity:
        return UserEntity(
            id=self.id,
            name=self.name,
            email=self.email,
            password=self.password,
            role=self.role,
            status=self.status,
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    @classmethod
    def from_entity(cls, entity: UserEntity) -> "AuthPostgresModel":
        role_val = entity.role.value if isinstance(entity.role, Role) else str(entity.role)
        status_val = entity.status.value if isinstance(entity.status, Status) else str(entity.status)
        return cls(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            password=entity.password,
            role=role_val,
            status=status_val,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
```

### `Features/Auth/Data/DataSources/AuthRepositoryPostegresSQL.py` (Excerpt)
```python
import logging
from sqlalchemy import select
from Core.DataBase.PostgresDB import SessionLocal
from Core.errors.AuthErrors import AuthError, UserAlredyExists, InvalidEmailOrPassword
from Core.errors.GlobleErrors import ServerError
from Core.security.Password import hash_password, verify_password
from Features.Auth.Data.Models.AuthModelPostgres import AuthPostgresModel
from Features.Auth.Domain.Entities.UserEntity import UserEntity
from Features.Auth.Domain.Repository.AuthRepository import AuthRepository

logger = logging.getLogger(__name__)

class AuthRepositoryPostgresSQl(AuthRepository):
    def __init__(self, db=None):
        self.db = db if db is not None else SessionLocal()

    async def create_user(self, email: str, name: str, password: str) -> UserEntity:
        try:
            existing = self.db.execute(
                select(AuthPostgresModel).where(AuthPostgresModel.email == email)
            ).scalars().first()

            if existing:
                raise UserAlredyExists()

            hashed_pwd = hash_password(password)
            user_model = AuthPostgresModel(
                email=email,
                name=name,
                password=hashed_pwd
            )
            self.db.add(user_model)
            self.db.commit()
            self.db.refresh(user_model)
            return user_model.to_entity()
        except AuthError:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            logger.exception(f"Error creating user: {email}")
            raise ServerError(detail=str(e))
```

---

## 4. Referenced In Master Architecture
- [Features Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-layer.md)
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
