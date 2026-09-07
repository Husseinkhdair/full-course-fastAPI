---
trigger: always_on
description: Rules and guidelines for constant string literals, roles, and statuses in Core/Strings/
---

# Core String Constants & Literals Rule (`Core/Strings/`)

## 1. Overview & Responsibility
The `Core/Strings/` package eliminates magic strings across business logic, database queries, and route authorization guards by providing typed, central string constants.

**Folder Location**: `Core/Strings/`
- `RoleString.py`

---

## 2. Mandatory Architectural Rules

1. **Zero Magic Strings**:
   - Role comparisons (`user.role == "admin"`), account statuses, and system keys MUST NOT use raw inline string literals.
   - Always import constants from `Core.Strings.*`.
2. **Naming Convention**:
   - Variables should be lower-case or UPPERCASE identifiers with explicit type annotations:
     ```python
     admin: str = 'admin'
     user: str = 'user'
     active: str = 'active'
     inactive: str = 'inactive'
     deleted: str = 'deleted'
     ```

---

## 3. Code Blueprint & Reference Implementation

### `Core/Strings/RoleString.py`
```python
# User Role Literals
admin: str = 'admin'
user: str = 'user'

# Entity Status Literals
active: str = 'active'
inactive: str = 'inactive'
deleted: str = 'deleted'
```

---

## 4. Referenced In Master Architecture
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
