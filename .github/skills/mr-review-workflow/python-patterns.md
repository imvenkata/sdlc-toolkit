# Python Code Review Patterns

Language-specific review patterns for Python codebases. Loaded by the Code Quality Reviewer sub-agent when Python files are detected in the MR.

---

## Type Hints & Annotations

### Positive Signals
- Function signatures include type hints for all parameters and return types
- Use of `Optional[T]`, `Union[T1, T2]`, or `T | None` (Python 3.10+)
- Complex types use `TypeAlias`, `TypeVar`, or `Protocol` for clarity
- `dataclasses` or `pydantic.BaseModel` used for structured data instead of raw dicts

### Negative Signals
- Functions missing type hints entirely (especially public APIs)
- Use of `Any` without justification
- `# type: ignore` without explanation comment
- Returning different types conditionally without `Union` annotation

---

## Error Handling

### Positive Signals
- Specific exception types caught (not bare `except:` or `except Exception:`)
- Custom exception classes for domain errors
- Context managers (`with`) for resource management (files, DB connections, locks)
- `logging.exception()` or `logger.error(..., exc_info=True)` in catch blocks

### Negative Signals
- Bare `except:` — swallows all exceptions including `KeyboardInterrupt`, `SystemExit`
- `except Exception: pass` — silently swallowed errors
- `try/except` around large code blocks (should be narrowly scoped)
- Missing `finally` for cleanup when not using context managers
- String formatting in exception messages without context (e.g., `raise ValueError("bad")`)

---

## Async / Concurrency

### Positive Signals
- `async def` with proper `await` on all coroutines
- `asyncio.gather()` for parallel I/O operations
- `async with` for async context managers
- Thread-safe data structures when using `threading`

### Negative Signals
- Blocking calls (`time.sleep()`, `requests.get()`) inside async functions
- Missing `await` on coroutines (returns coroutine object instead of result)
- `asyncio.run()` called inside an already-running event loop
- Shared mutable state without locks in threaded code

---

## Django Patterns

### Positive Signals
- Querysets use `.select_related()` / `.prefetch_related()` to avoid N+1
- Model fields have `help_text` and appropriate `verbose_name`
- Views use appropriate permission classes / decorators
- Migrations are atomic and reversible
- Form/serialiser validation before save

### Negative Signals
- N+1 queries: iterating queryset and accessing related objects without prefetch
- `Model.objects.all()` without pagination in views
- Raw SQL without parameterisation (`cursor.execute(f"SELECT ...")`)
- Missing `on_delete` on ForeignKey (or using `CASCADE` without thought)
- Business logic in views instead of model methods or service layer
- `settings.py` containing hardcoded secrets

---

## Flask / FastAPI Patterns

### Positive Signals
- Request validation via Pydantic models (FastAPI) or marshmallow schemas (Flask)
- Dependency injection for database sessions, auth, etc.
- Background tasks for long-running operations
- Proper HTTP status codes in responses

### Negative Signals
- `request.json` accessed without validation
- Database sessions not properly closed/committed
- Missing error handlers for common HTTP errors (404, 422, 500)
- Synchronous database calls in async FastAPI endpoints
- CORS configured with `allow_origins=["*"]` in production

---

## Pythonic Idioms

### Positive Signals
- List/dict/set comprehensions instead of manual loops for simple transformations
- `enumerate()` instead of manual index tracking
- `pathlib.Path` instead of `os.path` string manipulation
- `f-strings` for string formatting (Python 3.6+)
- `dataclasses` or `NamedTuple` instead of plain tuples for structured returns
- `contextlib.contextmanager` for custom context managers

### Negative Signals
- `len(x) == 0` instead of `not x` for truthiness checks
- Manual file open/close instead of `with open(...)`
- `dict.keys()` iteration when direct dict iteration suffices
- Mutable default arguments (`def f(x=[])`  — classic bug)
- String concatenation in loops (`+=`) instead of `"".join()`
- `import *` — pollutes namespace, hides dependencies

---

## Packaging & Dependencies

### Positive Signals
- Dependencies pinned with exact versions or compatible ranges in `requirements.txt` / `pyproject.toml`
- Dev dependencies separated from production dependencies
- `pyproject.toml` used for project metadata (PEP 621)
- Virtual environment documented / enforced

### Negative Signals
- Unpinned dependencies (`requests` instead of `requests>=2.28,<3`)
- `setup.py` without `pyproject.toml` (legacy pattern)
- System-level package installs (`pip install` without virtualenv)
- Missing `__init__.py` in packages (unless using namespace packages intentionally)

---

## Testing Patterns

### Positive Signals
- `pytest` fixtures used for setup/teardown
- Parametrised tests (`@pytest.mark.parametrize`) for multiple input cases
- Mocks scoped narrowly (`unittest.mock.patch` on specific targets)
- Async tests use `pytest-asyncio` with proper markers
- Test names describe the behaviour being tested

### Negative Signals
- Tests with no assertions (test does nothing useful)
- Mocking too broadly (patching entire modules)
- Tests that depend on execution order
- No cleanup of test data / side effects
- `print()` statements used for debugging instead of assertions
- Missing edge case tests (empty input, None, boundary values)

---

## Security (Python-Specific)

### Critical
- `pickle.loads()` on untrusted data — arbitrary code execution
- `yaml.load()` without `Loader=SafeLoader` — arbitrary code execution
- `subprocess.call(shell=True)` with user input — command injection
- `os.system()` with f-string user input — command injection
- `__import__()` or `importlib.import_module()` on user input

### Medium
- `tempfile.mktemp()` — race condition (use `tempfile.NamedTemporaryFile`)
- `hashlib.md5()` / `hashlib.sha1()` for security purposes (use sha256+)
- `random` module for security tokens (use `secrets` module)
- Logging f-strings with user data that could contain format strings
