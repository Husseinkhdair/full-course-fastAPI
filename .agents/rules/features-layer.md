---
trigger: always_on
description: Master architectural blueprint, directory layout, and component index for the Features layer in FastAPI clean architecture projects.
---

# Features Layer Master Architecture Blueprint

The **Features** layer encapsulates modular business domains of the application. Each feature is an autonomous vertical slice structured according to **Clean Architecture** and **Domain-Driven Design (DDD)** principles, separating pure business logic from persistence and presentation.

---

## 1. Directory Structure of a Feature

Every feature in `Features/<FeatureName>/` MUST strictly adhere to this three-tier internal architecture:

```text
Features/<FeatureName>/
│
├── Domain/                           # Pure business rules, agnostic of DB or Web
│   ├── Entities/                     # Pure Python domain entities and enums
│   │   └── <EntityName>Entity.py
│   ├── Repository/                   # Abstract repository interfaces (ports)
│   │   └── <FeatureName>Repository.py
│   └── UseCases/                     # Single-responsibility application workflows
│       ├── __init__.py               # Exports all UseCases
│       ├── Create<Entity>UseCase.py
│       └── ...
│
├── Data/                             # Persistence, schemas, and data adapters
│   ├── Models/                       # Database models with entity mappers
│   │   ├── <FeatureName>ModelPostgres.py  # SQLAlchemy ORM mapped model
│   │   └── <FeatureName>ModelMongos.py    # PyMongo document helper & serializer
│   └── DataSources/                  # Concrete repository implementations
│       ├── <FeatureName>RepositoryPostgresSQL.py # Relational data adapter
│       └── <FeatureName>RepositoryMongoDB.py     # NoSQL async data adapter
│
└── Presentation/                     # Web layer, HTTP routes, and serialization
    ├── route.py                      # FastAPI APIRouter and route handlers
    └── tdo.py                        # Pydantic DTOs (Request & Response schemas)
```

---

## 2. Specialized Rules & Component Map

The detailed rules, code blueprints, and implementation specifications for each layer inside a Feature are partitioned into dedicated rule files. Consult and adhere to each specialized rule file below:

| Feature Layer | Sub-Packages & Files | Dedicated Rule File | Rule Path |
| :--- | :--- | :--- | :--- |
| **Domain Layer** | `Domain/Entities/*`<br>`Domain/Repository/*`<br>`Domain/UseCases/*` | [features-domain.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-domain.md) | `.agents/rules/features-domain.md` |
| **Data Layer** | `Data/Models/*`<br>`Data/DataSources/*` | [features-data.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-data.md) | `.agents/rules/features-data.md` |
| **Presentation Layer** | `Presentation/route.py`<br>`Presentation/tdo.py` | [features-presentation.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-presentation.md) | `.agents/rules/features-presentation.md` |

---

## 3. Core Architectural Principles for Features

1. **Strict Dependency Flow**:
   - `Presentation` depends on `Domain` (UseCases, Entities, and DTO mappers).
   - `Data` depends on `Domain` (implements Repository interfaces, maps to/from Entities).
   - `Domain` depends on NOTHING in `Data` or `Presentation`. It is pure Python.
2. **Entity Isolation & Bidirectional Mapping**:
   - Entities must NEVER inherit from Pydantic `BaseModel` or SQLAlchemy `Base`.
   - Data models in `Data/Models/` must provide `to_entity()` and `@classmethod from_entity()`.
   - Response DTOs in `Presentation/tdo.py` must provide `@classmethod from_entity()`.
3. **Decoupled DI Wiring via `Core/di.py`**:
   - Route handlers in `route.py` must NEVER instantiate use cases or repositories directly.
   - For every new UseCase and Repository, provide dependency factory functions in `Core/di.py` and inject them via FastAPI `Depends()`.
4. **Dual-Database Support**:
   - Each feature must provide data adapters for both Relational (SQLAlchemy) and NoSQL (PyMongo) databases, selectable via `Core/di.py`.

---

## 4. Checklist for Creating a New Feature

When generating a new feature (e.g., `Features/Products/`), execute the following steps in order:

1. **Domain Layer**:
   - Create `Domain/Entities/<EntityName>Entity.py` with default UUID, UTC timestamps, and Enums from `Core.Strings.*`.
   - Define abstract repository interface in `Domain/Repository/<FeatureName>Repository.py` using `abc.ABC` and `@abstractmethod`.
   - Implement UseCases in `Domain/UseCases/` (e.g. `Create...UseCase.py`), handling validation, business logic, and error wrapping. Export them in `__init__.py`.
2. **Data Layer**:
   - Implement database models in `Data/Models/` with `to_entity()` and `from_entity()` conversions.
   - Implement concrete data sources in `Data/DataSources/` subclassing the domain repository for both Postgres and MongoDB.
3. **Dependency Injection**:
   - Add repository and use case provider functions in [Core/di.py](file:///c:/Users/dell-four/Desktop/test/Core/di.py).
4. **Presentation Layer**:
   - Define Pydantic request and response schemas in `Presentation/tdo.py` with `from_entity()` factory method.
   - Define endpoints in `Presentation/route.py` using `APIRouter(prefix="/<feature>", tags=["<Feature>"])` and inject use cases via `Depends()`.
5. **App Registration**:
   - Register the new router in [main.py](file:///c:/Users/dell-four/Desktop/test/main.py):
     ```python
     from Features.<FeatureName>.Presentation.route import router as <feature>_router
     app.include_router(<feature>_router)
     ```

---

## 5. Cross-Layer Architecture Reference
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
- [Core Dependency Injection Rule](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-di.md)
- [Core Error Handling Rule](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-errors.md)
- [Testing Master Architecture Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/testing-layer.md)
- [Application Bootstrap Rule](file:///c:/Users/dell-four/Desktop/test/.agents/rules/app-bootstrap.md)

