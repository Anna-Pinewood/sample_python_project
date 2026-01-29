# Project Guide

This document is the single source of rules and practices for the project. Our goal is a codebase that is **easy to read, navigate, diagnose, maintain and scale**.

---

## Contents

1. [Coding Standards](#1-coding-standards)
2. [Configuration Management](#2-configuration-management)
3. [Dependency Management](#3-dependency-management)
4. [Documentation & Status](#4-documentation--status)
5. [Testing](#5-testing)
6. [Python Conventions](#6-python-conventions)

---

## 1. Coding Standards

### Logging

- Use **lazy logging**:
  ```python
  logger.info("Received response: %s", response)
  ```
  Never use f-strings or `%` formatting inside logging calls.

- Logs should allow reconstructing execution path for debugging.

- Log levels:
  - `debug`: detailed internal state
  - `info`: high-level control flow
  - `warning`, `error`, `critical`: unexpected failures


### Type Hints

- Full type annotations are mandatory for public APIs.
- Use native Python 3.9+ types: `list[str]`, `dict[str, Any]`, `str | None`.
- Use `Literal[...]` for constrained values.

### Code Structure

- Modular, composable, readable, scalable, and testable code.
- Prefer pure functions.
- I/O and side effects behind well-defined service layers.
- Extract helpers after the third repetition ("rule of three").
- Follow PEP8.
- **Avoid over-engineering**: if splitting introduces verbosity or redundant abstractions — reconsider.

---

## 2. Configuration Management

### Single Source of Truth

- Use **one main config** (`config.yaml`) in project root.
- Add new sections to existing config instead of creating separate files.

### Config Structure

```yaml
# config.yaml
database:
  clickhouse:
    host: "localhost"
    port: 9000
    user: "${CLICKHOUSE_USER}"
    password: "${CLICKHOUSE_PASSWORD}"

paths:
  base_output: "/data/artifacts"
  logs: "logs"

# Script-specific
my_script:
  batch_size: 1000
  region_id: 1
```

### Using Config in Code

```python
from pydantic import BaseModel
from conf import CFG

class ScriptConfig(BaseModel):
    batch_size: int
    region_id: int

config = ScriptConfig(**CFG.my_script)
```

### Environment Variables

- Use env variables for sensitive data (passwords, API keys).
- Reference them in config via `${VAR_NAME}` syntax.
- Keep `.env.example` up to date with the current `.env` file.
---

## 3. Dependency Management

- Use **[uv](https://github.com/astral-sh/uv)** exclusively:
  ```bash
  uv venv .venv
  uv pip install -e ".[dev]"
  ```

---

## 4. Documentation & Status

### Status File (docs/status.md)

Keep `docs/status.md` up to date — it's the single source of truth for project progress.

**Format:**
```markdown
# Project Status

## Current State
Brief description of what works and what's in progress.

## Recent Changes
- YYYY-MM-DD: What was done (1-2 sentences)
- YYYY-MM-DD: What was done

## Next Steps
- [ ] Task 1
- [ ] Task 2
```

**Rules:**
- Keep it **concise but clear** — someone should understand project state in 60 seconds
- Update after each meaningful change
- Recent changes: max 10 entries, oldest get removed
- No implementation details — just outcomes

---

## 5. Testing

### End-to-end Examples

- After changes, add **brief snippets** for validation:
  - Create minimal representative input
  - Describe expected result
  - Cover happy-path and one edge-case

### Running Scripts

```bash
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:${PWD}/src
python src/script.py
```

---

## 6. Python Conventions

Detailed Python coding conventions are in [CONVENTIONS.md](./CONVENTIONS.md).

**Key rules:**

| Topic | Rule |
|-------|------|
| Type hints | `str \| None`, `list[int]` — modern syntax |
| Match/case | For type dispatch instead of `isinstance` chains |
| Naming | Descriptive names; `HTTPClient` in classes, `http_client` in variables |
| Constants | Named constants instead of magic numbers |
| Models | Pydantic for validation, `StrEnum` for string constants |
| Errors | Specific exceptions, never bare `except:` |
| Paths | `pathlib.Path` instead of `os.path` |
| Comments | Explain "why", not "what" |

---

## When in Doubt…

1. **Prefer explicitness** over hidden magic.
2. **Fail early** — raise, don't silently repair.
3. **Write the log you'd want** when debugging at 3 AM.
4. **Add to existing config** instead of creating new files.

---

Happy hacking — may your graphs be acyclic and your logs enlightening.
