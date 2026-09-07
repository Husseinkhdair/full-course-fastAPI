---
trigger: always_on
description: Rules and guidelines for structured JSON logging and contextual request tracing in Core/logging_config.py
---

# Core Logging & Tracing Rule (`Core/logging_config.py`)

## 1. Overview & Responsibility
The `logging_config.py` module establishes centralized, structured JSON logging and request tracing across asynchronous contexts using Python's `contextvars`.

**File Location**: `Core/logging_config.py`

---

## 2. Mandatory Architectural Rules

1. **Structured JSON Format**:
   - Always use `pythonjsonlogger.jsonlogger.JsonFormatter` with standard schema fields:
     `['asctime', 'levelname', 'name', 'user_id', 'request_id', 'message']`.
2. **Context Variables (Tracing)**:
   - Define async-safe context variables:
     ```python
     request_id_var = ContextVar('request_id', default=None)
     user_id_var = ContextVar('user_id', default=None)
     ```
3. **Dynamic Context Filter (`LoggerFilter`)**:
   - Implement a custom `logging.Filter` that dynamically pulls values from `user_id_var.get()` and `request_id_var.get()` and injects them onto the record object.
4. **Handler Configuration (`setup_logging()`)**:
   - **Root Logger Level**: Must be set to `DEBUG`.
   - **Console Handler**: `logging.StreamHandler()` with level `INFO`.
   - **File Handler**: `logging.FileHandler("app.json")` with level `DEBUG`, equipped with `LoggerFilter`.
   - **Noise Suppression**: Suppress chatty 3rd-party loggers (e.g. `logging.getLogger("pymongo").setLevel(logging.WARNING)`).
   - **Duplicate Handler Guard**: If `logger.handlers` is already populated, return immediately to prevent duplicate logging records.

---

## 3. Code Blueprint & Reference Implementation

```python
import logging
from pythonjsonlogger import jsonlogger
from contextvars import ContextVar

request_id_var = ContextVar('request_id', default=None)
user_id_var = ContextVar('user_id', default=None)

formatter = jsonlogger.JsonFormatter(
    ['asctime', 'levelname', 'name', 'user_id', 'request_id', 'message']
)

class LoggerFilter(logging.Filter):
    def filter(self, record):
        record.user_id = user_id_var.get()
        record.request_id = request_id_var.get()
        return True

def setup_logging():
    logging.getLogger("pymongo").setLevel(logging.WARNING)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler("app.json")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    file_handler.addFilter(LoggerFilter())

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
```

---

## 4. Referenced In Master Architecture
- [Core Master Blueprint](file:///c:/Users/dell-four/Desktop/test/.agents/rules/core-layer.md)
