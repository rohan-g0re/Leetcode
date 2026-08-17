# Glossary

Every term this course uses, in plain language. Skim it now; come back when a lesson uses
a word you're unsure of.

## Python language

**Interpreter** — the `python.exe` program that reads your `.py` file and executes it.

**Object** — every value in Python is an object: numbers, strings, lists, functions,
even classes. "Object" just means "a thing with a type and some behavior."

**Type** — the kind of a value: `int`, `str`, `list`, `dict`. Check with `type(x)`.

**Variable** — a *name bound to an object*. Not a box holding a value — a label pointing
at one. `a = b` makes both names point at the same object; it does not copy.

**Mutable / immutable** — mutable objects can be changed in place (`list`, `dict`, `set`).
Immutable ones cannot (`int`, `str`, `tuple`); "changing" them creates a new object.

**Iterable** — anything you can loop over with `for`: lists, strings, dicts, files,
generators.

**Statement vs expression** — an expression produces a value (`2 + 2`, `f(x)`). A
statement does something (`if`, `for`, `x = 5`). Expressions can go where values go.

**Function** — a named, reusable block. `def name(params): ...`, produces a value with
`return`. A function with no `return` returns `None`.

**Argument vs parameter** — parameters are the names in the `def`; arguments are the
values you actually pass at the call site.

**Scope** — the region where a name is visible. Names created inside a function are local
to it and vanish when it returns.

**Module** — one `.py` file. **Package** — a folder of modules. Both are brought in with
`import`.

**Standard library** — modules that ship with Python, no install needed: `json`, `os`,
`datetime`, `collections`, `statistics`, `pathlib`.

**Exception** — an error object raised when something goes wrong. Unhandled, it stops the
program and prints a traceback.

**Traceback** — the stack of function calls printed on an unhandled exception. Read it
bottom-up.

**`None`** — the "no value" object. Distinct from `0`, `""`, and `False`.

**Truthy / falsy** — non-boolean values used in a boolean context. Falsy: `False`, `None`,
`0`, `0.0`, `""`, `[]`, `{}`, `set()`. Everything else is truthy.

**f-string** — `f"total: {x}"`. Embeds expressions in a string literal.

**Comprehension** — `[f(x) for x in xs if cond]`. Builds a list (or dict/set) in one
expression instead of a loop with `.append`.

**`lambda`** — a tiny anonymous function: `lambda x: x["age"]`. Used as a `key=` argument.

**Decorator** — `@something` above a `def`. A function that wraps another function.
`@app.get("/x")` in FastAPI registers your function as a route handler.

**Type hint** — annotation like `def f(x: int) -> str:`. Python does **not** enforce them
at runtime; they're for readers, editors, and tools like Pydantic (which *does* enforce).

**`__name__ == "__main__"`** — true only when the file is run directly, false when it's
imported. Guards code that should only run as a script.

**Virtual environment (venv)** — an isolated per-project package directory.

## HTTP & APIs

**API** — Application Programming Interface. Here: a server that returns machine-readable
data (usually JSON) over HTTP instead of a web page.

**REST** — a style where URLs identify resources (`/users/42/repos`) and HTTP methods
describe the action. Most "APIs" you'll meet are loosely REST.

**Endpoint** — one specific URL + method combination the API responds to.

**URL parts** — `https://api.example.com/v1/users?limit=10&sort=name#frag`:
scheme (`https`), host (`api.example.com`), path (`/v1/users`), query string
(`limit=10&sort=name`), fragment (never sent to the server).

**Query parameters** — the `key=value` pairs after `?`. Filtering, paging, sorting.

**Path parameters** — variable segments *inside* the path: `/users/{username}`.

**HTTP method (verb)** — `GET` (read), `POST` (create/submit), `PUT`/`PATCH` (update),
`DELETE` (remove).

**Header** — metadata key/value on a request or response. `Content-Type`, `Authorization`,
`User-Agent`, `Retry-After`, `X-RateLimit-Remaining`.

**Body / payload** — the data part. `GET` requests usually have none; `POST` carries one.

**Status code** — 3-digit result. 2xx success, 3xx redirect, 4xx your fault, 5xx their fault.

**JSON** — JavaScript Object Notation. Text format for nested data. Maps onto Python:
object→`dict`, array→`list`, string→`str`, number→`int`/`float`, `true`/`false`→`True`/`False`,
`null`→`None`.

**Serialize / deserialize** — Python object → JSON text (`json.dumps`) and back
(`json.loads`). "Parsing" = deserializing.

**Rate limit** — a cap on requests per time window. Exceeded → 429 (or 403 on GitHub).

**Pagination** — splitting a large result set across responses. Offset-based, cursor-based,
or `Link`-header-based.

**Idempotent** — repeating the request has the same effect as doing it once. `GET` is;
`POST` usually isn't. Matters when deciding what's safe to retry.

**Timeout** — max seconds to wait. Without one, a hung server hangs your program forever.

**Backoff** — waiting progressively longer between retries (1s, 2s, 4s).

**Session** — a reusable client object that keeps connections alive and shares headers
across requests.

## Data analysis

**Record / row** — one entity. In JSON, usually one dict in a list.

**Field / column** — one attribute across all records.

**Flatten / normalize** — turn nested JSON (`{"a": {"b": 1}}`) into flat columns (`a.b`).

**Aggregate** — collapse many rows into one number: sum, mean, count, max.

**Group by** — split rows by a categorical field, aggregate each group.

**Join / merge** — combine two tables on a shared key.

**DataFrame** — pandas' 2-D table. Columns can each have their own type.

**Series** — one pandas column; a 1-D labeled array.

**Index** — a DataFrame's row labels. Not the same as a positional index.

**NaN** — "not a number"; pandas' missing-value marker for numeric columns.

**dtype** — a column's data type (`int64`, `float64`, `object`, `datetime64[ns]`).
`object` usually means "strings, or mixed junk."

**Vectorized** — an operation applied to a whole column at once by pandas' C internals,
rather than by a Python loop. Much faster and the idiomatic way to write pandas.

**Skew** — asymmetry in a distribution. Mean far above median = right-skewed.

## FastAPI

**Framework** — library that provides the structure of an application; you fill in the
gaps. FastAPI handles HTTP, routing, validation, and docs.

**ASGI** — the modern Python web-server interface, supporting `async`. FastAPI is an ASGI
app; `uvicorn` is the ASGI server that runs it.

**uvicorn** — the process that binds a port and feeds requests to your app.

**Route / path operation** — a URL+method bound to one of your functions.

**Route handler** — the function that runs for a route.

**Pydantic model** — a class declaring a data shape with type hints. FastAPI uses it to
parse, validate, and document request and response bodies.

**Validation** — checking incoming data matches the declared shape. Failure → automatic
422 with a precise error, written by FastAPI, not you.

**`response_model`** — declares the output shape; FastAPI filters and validates what you
return against it. Useful for not leaking internal fields.

**Dependency injection** — declaring "this route needs X" via `Depends(...)`; FastAPI
builds X and passes it in. Used for shared clients, config, and auth.

**`async` / `await`** — lets one process handle many in-flight I/O operations
concurrently. `await` means "pause here and let other work run until this finishes."

**Coroutine** — what an `async def` function returns when called. Does nothing until
awaited.

**Blocking call** — one that stops the whole event loop (e.g. `requests.get` or
`time.sleep` inside an `async def`). Use `httpx` + `asyncio.sleep` instead.

**OpenAPI / Swagger** — the machine-readable API description FastAPI generates for free,
rendered as an interactive page at `/docs`.

**`TestClient`** — calls your FastAPI app in-process, no server, no network. How you test.

## Testing

**pytest** — the test runner. Collects functions named `test_*` and runs them.

**Assertion** — `assert expr`. Passes silently if true; fails the test if not.

**Fixture** — reusable setup, requested by naming it as a test parameter.

**Marker** — a tag on a test (`@pytest.mark.live`) for selecting or skipping groups.

**Parametrize** — run one test function against many inputs.
