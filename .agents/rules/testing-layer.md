---
trigger: always_on
description: Master architectural blueprint, test pyramid hierarchy, and component index for testing in FastAPI clean architecture projects.
---

# Testing Layer Master Architecture Blueprint

The **Tests** layer ensures the reliability, correctness, and security of the application across every layer of the architecture. It follows the **Testing Pyramid** methodology, separating tests into three distinct scopes: **Unit**, **Integration**, and **End-to-End (E2E)**.

---

## 1. Directory Structure

Any test suite adhering to this architecture MUST follow this exact directory structure under `Tests/`:

```text
Tests/
│
├── Unit/                             # Isolated in-memory tests (No DB, mocked UseCases)
│   ├── <FeatureName>/
│   │   ├── test_<feature>_models.py  # Model/Entity mapping & attribute verification
│   │   └── test_<feature>_routes.py  # Route controller tests via dependency_overrides
│   └── Core/
│       ├── DataBase/                 # Client resolution & proxy behavior
│       ├── security/                 # Password hashing & JWT token verification
│       ├── test_di.py                # DI provider resolution
│       └── test_settings.py          # SettingsApp loading & validation
│
├── Integration/                      # Real database & interconnected component testing
│   └── <FeatureName>/
│       ├── DataSoruces/              # Concrete SQL & NoSQL repository queries
│       ├── UseCases/                 # Use cases orchestrating real repositories
│       └── Presentation/             # Full HTTP route flows with live databases
│
└── E2E/                              # Multi-step complete user journeys & isolation
    └── test_<feature>_e2e.py         # End-to-end lifecycle, tokens, and error cases
```

---

## 2. Specialized Rules & Component Map

The detailed rules, fixtures, assertions, and implementation specifications for each testing tier are partitioned into dedicated rule files. Consult and adhere to each specialized rule file below:

| Testing Tier | Target Directory / Scope | Dedicated Rule File | Rule Path |
| :--- | :--- | :--- | :--- |
| **Unit Testing** | `Tests/Unit/*` | [test-unit.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/test-unit.md) | `.agents/rules/test-unit.md` |
| **Integration Testing** | `Tests/Integration/*` | [test-integration.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/test-integration.md) | `.agents/rules/test-integration.md` |
| **End-to-End (E2E) Testing** | `Tests/E2E/*` | [test-e2e.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/test-e2e.md) | `.agents/rules/test-e2e.md` |
| **Application Bootstrap** | `main.py` | [app-bootstrap.md](file:///c:/Users/dell-four/Desktop/test/.agents/rules/app-bootstrap.md) | `.agents/rules/app-bootstrap.md` |

---

## 3. Global Testing Configuration (`pytest.ini`)

All tests operate under standard pytest configuration defined in `pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
markers =
    integration: integration tests
    e2e: end-to-end tests
```

### Execution Commands:
- **Run All Tests**: `pytest`
- **Run Unit Tests Only**: `pytest Tests/Unit`
- **Run Integration Tests Only**: `pytest -m integration`
- **Run E2E Tests Only**: `pytest -m e2e`

---

## 4. Fundamental Testing Principles

1. **Strict Tier Isolation**:
   - **Unit Tests** must NEVER connect to external databases or services; always use mocks (`unittest.mock.AsyncMock`) and `app.dependency_overrides`.
   - **Integration Tests** verify real queries and mutations; always clean up data created during tests.
   - **E2E Tests** simulate real client journeys through the public API surface.
2. **Deterministic Cleanup**:
   - Tests that insert records into databases must guarantee teardown deletion via `finally` blocks or fixtures.
   - Tests overriding FastAPI dependencies must always call `app.dependency_overrides.clear()`.
3. **Async Event-Loop Safety**:
   - Any test invoking asynchronous functions must be defined as `async def test_*`.
   - With `asyncio_mode = auto`, pytest automatically handles the event loop.

---

## 5. Cross-Layer Architecture Reference
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
- [Features Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/features-layer.md)
- [Application Bootstrap Rule](file:///c:/Users/dell-four/Desktop/test/.agents/rules/app-bootstrap.md)
