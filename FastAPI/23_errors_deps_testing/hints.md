# Unit 23 — hints

*Open this after about ten minutes of genuinely trying a piece — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished endpoint. The sections are in file order, so you can drop in wherever you are.*

---

### `UpstreamError`

An exception class is an ordinary Python class that inherits from `Exception`. All you are adding is an `__init__` that records two attributes:

```python
class UpstreamError(Exception):
    def __init__(self, kind, context=""):
        super().__init__(f"{kind}: {context}")
        self.kind = kind
        self.context = context
```

The `super().__init__(...)` line calls the parent `Exception`'s own initialiser with a message. That is what makes `str(exc)` produce something readable, which is what ends up in your log file when the exception is printed. Skip it and the exception logs as an empty pair of brackets, and you learn nothing from the incident.

The two attributes are just attributes; the tests read them as `exc.kind` and `exc.context`.

---

### `get_client`

Two lines, and the shape is the same `async with` you used in unit 22, except the client escapes the block through a `yield` instead of being used inside it:

```python
async def get_client():
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        yield client
```

The function pauses at the `yield` while your endpoint runs. When the response has been produced, execution resumes, falls off the end of the `async with`, and the context manager closes the client. That is the guaranteed cleanup, and it is why `return` would be wrong — a `return` ends the function immediately, and the `async with` would close the client before your endpoint had even started with it.

---

### `pagination`

The body really is one line:

```python
return {"limit": limit, "offset": offset}
```

Everything else is already written, in the signature you were given. Resist the urge to add validation inside the function; the `Query(default=10, ge=1, le=100)` and `Query(default=0, ge=0)` declarations are the validation, and they run before your function does. If you write an `if limit > 100` check you will never see it fire, because FastAPI has already sent the 422.

---

### `require_api_key`

Read the environment variable inside the function, on the first line, then work through the three cases in order:

```python
expected = os.environ.get(API_KEY_ENV)
if not expected:
    return None
...
```

`if not expected` covers both "unset" and "set to an empty string" at once, because `None` and `""` are both falsy — unit 01's truthiness rules doing exactly the job they exist for. Below that, compare `x_api_key` against `expected` and `raise HTTPException(status_code=401, detail="invalid or missing api key")` when they differ, otherwise return the key.

Note that the mismatch branch also catches the missing header, since `x_api_key` is `None` when no header was sent and `None` never equals a real key. You do not need a separate check for it.

If you find yourself wanting `EXPECTED = os.environ.get(API_KEY_ENV)` at the top of the module: that is the mistake the docstring warns about. Module-level code runs once at import, before any test has set the variable, and the value is frozen from then on.

---

### The exception handler

You could write six `if` statements. A lookup table is shorter, and it puts the entire mapping in one place you can read at a glance:

```python
ERROR_MAP = {
    "not_found": (404, "not found: {context}"),
    "rate_limited": (429, "upstream rate limited"),
    ...
}


@app.exception_handler(UpstreamError)
async def handle_upstream_error(request, exc):
    status, template = ERROR_MAP.get(exc.kind, (502, "upstream error"))
    return JSONResponse(
        status_code=status,
        content={"detail": template.format(context=exc.context), "kind": exc.kind},
    )
```

Two small things make that work. The `.get(key, default)` supplies the "anything else" row from the table without a special case — unit 04's `.get()` again, and the reason the handler cannot crash on a kind you never anticipated. And calling `.format(context=...)` on a template that contains no `{context}` placeholder is simply harmless: it returns the string unchanged. So one line handles both the row that interpolates and the five that don't.

`JSONResponse` is already imported at the top of the file.

---

### The middleware

Take a reading, run the rest of the app, take another reading, attach the difference:

```python
@app.middleware("http")
async def add_timing_header(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - started:.4f}"
    return response
```

The `:.4f` inside the f-string is what gives you four decimal places. The header name is checked exactly, including its capitalisation as written here, and the test parses the value with `float()`, so it has to be a bare number with no unit suffix.

Forgetting the final `return response` is the classic mistake and produces a confusing failure — the request appears to hang or the caller receives nothing — because you have swallowed the response rather than passing it on.

---

### `fetch`

One `try` holding the three happy-path lines, then three `except` clauses in this order: `httpx.HTTPStatusError`, then `httpx.TimeoutException`, then `httpx.RequestError`.

```python
try:
    response = await client.get(f"{GITHUB}{path}", params=params)
    response.raise_for_status()
    return response.json()
except httpx.HTTPStatusError as exc:
    status = exc.response.status_code
    ...
```

Inside the first clause, branch on `exc.response.status_code`: 404 gives you `"not_found"`, 429 gives `"rate_limited"`, and anything else falls through to `"bad_response"`. Two `if`s and a final unconditional raise, no `else` needed.

The ordering is the thing to get right and the thing an interviewer might poke at. `HTTPStatusError` is not a `RequestError` — different branch of the tree entirely, because "they answered with a bad status" and "they did not answer" are different events. But `TimeoutException` *is* a subclass of `RequestError`, so putting `RequestError` above it means the broad clause matches first and every timeout is mislabelled as unavailable. Python takes the first matching clause, always, so specific goes above general.

Raise with `from exc`:

```python
raise UpstreamError("timeout", context) from exc
```

which keeps the original httpx exception in the traceback as the cause.

---

### `slim_repo`

A single dictionary literal built from four `.get()` calls. Two of them need care.

`repo.get("stargazers_count") or 0` rather than `repo.get("stargazers_count", 0)`, because the default form only applies when the key is *absent* — if GitHub sends the key holding `null`, the default is skipped and you get `None` through into your output. `or 0` catches both, since `None` is falsy. That's unit 04's `or {}` idiom in numeric clothing.

`bool(repo.get("archived"))` for the last one. The spec says a bool, and `.get()` on a missing key gives `None`, which is not `False` — it would serialise into your JSON as `null` and a client checking `if repo.archived` in another language might well disagree with you about what that means.

---

### The endpoints

Every protected endpoint takes its pieces as parameters:

```python
client: httpx.AsyncClient = Depends(get_client),
page: dict = Depends(pagination),
_key: str | None = Depends(require_api_key),
```

The underscore on `_key` signals that you are obliged to accept the value but do not intend to use it — you want the check to run, and the check happens whether or not you look at what comes back. `/users/{username}` takes only the first and third of those, since it has nothing to page.

`/health` takes none of them at all, which is exactly what makes it usable by a monitor that has no credentials.

For the ranking that three endpoints share, one small helper keeps it honest:

```python
def _ranked(repos):
    return sorted(repos, key=lambda r: (-r["stars"], r["name"] or ""))
```

Negating the stars turns ascending order into descending; the name stays positive so equal star counts fall back to alphabetical. The `or ""` guards against a repo with a null name, since Python refuses to compare `None` with a string and would raise a `TypeError` mid-sort.

Paging is one slice:

```python
window = items[page["offset"] : page["offset"] + page["limit"]]
```

Slicing never runs off the end, so an offset past the last item gives you an empty list rather than an error, and you need no bounds check.

Then assemble the response dictionary with exactly the keys the spec lists. `total` is `len(items)` — the count *before* paging — while `count` is `len(window)`. Getting those two the wrong way round is the easy slip, and both tests check them.

The one exception is `/search/repos`, where `total` comes from `payload.get("total_count")` and not from `len(items)`. That is the whole point of that endpoint's test, which even says so in its assertion message. The items you page still come from `payload.get("items") or []` — the `or []` because a search matching nothing may send you an empty list or nothing at all, and you cannot iterate over `None`.
