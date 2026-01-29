
# Python Coding Conventions

This project follows strict Python conventions documented in [CONVENTIONS.md](.cursor/CONVENTIONS.mdc).

## Style Requirements

### Pattern Matching
- **USE** `match/case` for working with weakly structured data and type dispatching
- **USE** `match/case` with classes for simultaneous type checking and destructuring
- **AVOID** chains of `isinstance()` checks when pattern matching is appropriate

### Type Hints
- **USE** modern PEP 604 syntax: `str | None`, `list[int]`, `dict[str, int]`
- **USE** abstract types in function parameters: `Sequence[str]`, `Mapping[str, int]`
- **NEVER** use `from __future__ import annotations` (Python 3.13+ has native support)
- **MANDATORY** type hints for all public APIs (functions, methods, classes)
- **AVOID** legacy typing: `Optional`, `Union`, `List`, `Dict`

### Naming Conventions
- **USE** descriptive variable names that convey semantics, not form
- **CLASSES**: Abbreviations in PascalCase use all caps: `HTTPClient`, `APIHandler`, `XMLParser`
- **VARIABLES/FUNCTIONS**: Abbreviations in snake_case use lowercase: `http_client`, `api_key`, `xml_content`
- **NUMBERS**: No extra underscores before numbers: `http2_protocol`, `base64_encoder`, `ipv6_address`

### Code Quality
- **NO** magic numbers - use named constants with semantic meaning
- **USE** comprehensions for simple transformations (≤2 nesting levels)
- **USE** explicit loops for complex logic or deep nesting (>2 levels)
- **USE** `NamedTuple` for functions returning multiple values
- **USE** f-strings exclusively for string formatting
- **AVOID** reflection (`getattr`, `hasattr`) - prefer explicit Pydantic schemas

### Destructuring
- **USE** tuple unpacking: `x, y = point`
- **USE** `match/case` for declarative extraction from complex structures

## Project Structure

### Models & Validation
- **ALL** Pydantic models must be declared in `app/models/`
- **USE** `ConfigDict` for model configuration
- **USE** Pydantic for validation at service boundaries

### Enums
- **USE** `StrEnum` from `enum` module for string constants
- **EXPLICITLY** define string values, don't rely on `auto()`
- **DECLARE** enums in `app/enums/`

### Error Handling
- **DEFINE** custom exceptions in `app/errors.py`
- **CATCH** specific exceptions only (e.g., `ValueError`, `FileNotFoundError`)
- **NEVER** use `except Exception:` unless absolutely necessary with logging
- **NEVER** use bare `except:` - it catches system exceptions

### Logging
- **USE** structured logging via `from app.logger import logger`
- **PROVIDE** context in log messages, don't format manually
- **LEVELS**: `logger.debug()`, `logger.info()`, `logger.warning()`, `logger.error()`

## Code Cleanliness

### Comments
- **EXPLAIN** "why", not "what"
- **DOCUMENT** invariants, trade-offs, and non-standard decisions
- **AVOID** stating the obvious

### File Operations
- **USE** `pathlib.Path` instead of `os.path`
- **EXAMPLE**: `Path(__file__).parent / "config" / "app.yaml"`

## Examples

### Good Pattern Matching
```python
from app.enums import Status

match response:
    case SuccessResponse(status=Status.OK, data=data):
        return f"Success: {data}"
    case ErrorResponse(error=error, code=code) if code >= 500:
        return f"Server error {code}: {error}"
    case ErrorResponse(error=error, code=code):
        return f"Client error {code}: {error}"
    case _:
        return "Unknown response"
```

### Good Type Hints
```python
from typing import Sequence, Mapping

def process_items(items: Sequence[str], cache: Mapping[str, int]) -> str | None:
    first: str | None = next(iter(items), None)
    return first
```

### Good NamedTuple Usage
```python
from typing import NamedTuple

class UserStats(NamedTuple):
    posts_count: int
    average_rating: float
    is_verified: bool

def get_user_stats(user_id: int) -> UserStats:
    return UserStats(
        posts_count=get_posts_count(user_id),
        average_rating=calculate_rating(user_id),
        is_verified=check_verification(user_id)
    )
```

### Good Error Handling
```python
try:
    result = int(user_input)
except ValueError:
    raise ValidationError("user_input", user_input, "must be a valid integer")

try:
    data = load_json_file(f"data_{result}.json")
except FileNotFoundError:
    logger.warning(f"Data file for {result} not found, using defaults")
    data = get_default_data()
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in data_{result}.json: {e}")
    raise DataCorruptionError(f"data_{result}.json")
```

## Reference
For detailed explanations and more examples, see [CONVENTIONS.md](conventions/CONVENTIONS.md).
