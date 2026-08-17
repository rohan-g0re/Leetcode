# 23 — Errors, Dependencies, and Testing

*This is the last teaching unit of the course. After this there are two capstones and a set of drills, and both capstones assume everything here. Read it straight through — about twenty-five minutes — then open `task.py`, which takes about the same again. Nothing is assumed beyond units 20, 21, and 22.*

*The occasion is worth naming, because it shapes what this lesson emphasises. If an interviewer asks you to wrap somebody else's API in a service of your own, unit 22 got you to something that works. This unit gets you to something you could hand to another person and let them maintain. Those are different bars, and the second one is the one that gets remembered.*

---

## 1. What is actually wrong with what you built in unit 22

You finished unit 22 with a working gateway. It called GitHub, it reshaped the response, it caught the network failures, it returned sensible status codes. If you ran it, it worked. So it's fair to ask what's left.

Three things, and they're all the same kind of problem wearing different clothes.

**First, the client was a global.** Unit 22's `get_client()` was a plain module-level function that every other function called, and the tests had to reach into your module and swap that function out — `monkeypatch.setattr(task, "get_client", ...)`. That works, but notice what it means: your test had to know the name of an internal function and go behind your code's back to replace it. Your code had no idea it was being tested, and there was no place in it that said "this is the bit you're allowed to substitute."

**Second, your service functions knew about HTTP.** In unit 22 you wrote `upstream_error`, which took an `httpx` exception and handed back an `HTTPException` with a status code attached. That's translation happening *inline*, right next to the fetching. It's fine as far as it goes, but it means the function that talks to GitHub also has an opinion about what your callers should see, and those are two genuinely different concerns.

**Third, nothing said what "correct" meant.** You had tests, and they were decent, but they existed because the course wrote them. You hadn't yet been shown the two or three tests that earn their keep in an interview, or the fixture pattern that stops tests poisoning each other.

This unit fixes all three, and the fix for the first one turns out to be the fix for the third one too. That's the connection worth watching for as you read.

---

## 2. Dependency injection, built from the problem

I want to arrive at the syntax rather than start with it, because starting with `Depends(...)` makes it look like FastAPI trivia when it's actually an architectural idea you'll meet in every language you ever work in.

### 2.1 The problem

Your handler for `/users/{username}` needs an HTTP client to call GitHub with. Where does it come from?

You have three options and two of them are bad. You could build one inside the handler, which is what unit 22's first sketch did — but then every request constructs a fresh client and throws away the connection pooling, and there's no way to test the handler without real network. You could make one global client at module level — faster, but now it's a shared mutable thing created at import time, impossible to swap, and it has to be torn down by somebody who remembers to.

The third option is the one this unit is about: **the handler declares what it needs and lets something else decide what that is.**

### 2.2 What a dependency is

A **dependency**, in FastAPI's sense, is just a function whose return value FastAPI passes into your handler as an argument. **Dependency injection** is the name for that arrangement in general — the thing you need is handed *to* you (injected) rather than fetched *by* you.

```python
from fastapi import Depends

def get_settings():
    return {"page_size": 50}


@app.get("/items")
def list_items(settings: dict = Depends(get_settings)):
    return {"page_size": settings["page_size"]}
```

Read that carefully because there's one genuinely unusual thing happening. The parameter `settings` has a default value of `Depends(get_settings)`. That is not a real default — `Depends` is a marker. When a request arrives, FastAPI sees the marker, calls `get_settings()` itself, and passes the result in as `settings`. Notice you never wrote `get_settings()` anywhere with parentheses; you handed FastAPI the function itself and let *it* do the calling. That distinction between naming a function and calling it comes straight out of unit 07, where you passed a function to `sorted(key=...)` the same way.

And notice what the caller sees: nothing. Somebody hitting `/items` sends a plain GET with no parameters. The dependency is invisible from outside.

The mental model to carry: **a dependency is a seam.** It's a deliberate cut in your application at a point where you might one day want to put something different — a fake, a stub, a different implementation. Everything in this section is about where to put the seams.

### 2.3 The first thing it buys you: a shared resource that always gets cleaned up

Here is the shape you'll use in the task:

```python
async def get_client():
    async with httpx.AsyncClient(timeout=10) as client:
        yield client


@app.get("/user/{name}")
async def user(name: str, client: httpx.AsyncClient = Depends(get_client)):
    ...
```

That `yield` instead of `return` is doing real work, and it deserves a name. A **generator dependency** is a dependency that hands over its value with `yield` rather than `return`. FastAPI runs everything *before* the `yield` on the way into your handler, hands you the yielded value, lets your handler run, and then — once the response has been produced — comes back and runs everything *after* the `yield`.

So the `async with` block opens the client on the way in and closes it on the way out, and the closing is guaranteed. It happens whether your handler returned normally or blew up halfway through. This is exactly the `with` statement from unit 09, which you used so a file always got closed, except stretched across the whole request instead of a few lines.

That's why the docstring in `task.py` insists on `yield`. Write `return httpx.AsyncClient(...)` instead and you get a client that is never closed, one per request, leaking connections quietly until the process runs out of file descriptors under load. Nothing will fail in your tests. It'll fail on a Tuesday afternoon in production.

### 2.4 The second thing: validated parameters written once

Unit 20 taught you `Query` with constraints — `Query(default=10, ge=1, le=100)` means "an integer, defaulting to 10, at least 1, at most 100," and FastAPI rejects anything else with a 422 before your code runs. That's great until three endpoints all need paging and you copy the same two parameters into all three.

A dependency solves it, because a dependency function has a signature of its own and FastAPI reads it the same way it reads a handler's:

```python
def pagination(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return {"limit": limit, "offset": offset}


@app.get("/a")
def a(page: dict = Depends(pagination)): ...

@app.get("/b")
def b(page: dict = Depends(pagination)): ...
```

Both endpoints now accept `?limit=&offset=`, both enforce the same ranges, both document them identically on the `/docs` page, and the rule lives in exactly one place. If you later decide the maximum should be 200, you change one number.

This is the same instinct as unit 06's fetch-and-transform split, moved up one level. There you separated "get the data" from "reshape the data" so each piece could be tested and reused on its own. Here you're separating "work out what this request is asking for" from "answer it." Same move, bigger unit of work.

### 2.5 The third thing: auth, because a dependency can refuse

A dependency isn't obliged to return anything. It can raise instead, and if it does, **your handler never runs at all.**

```python
def require_token(x_api_key: str | None = Header(default=None)):
    if x_api_key != "secret":
        raise HTTPException(status_code=401, detail="invalid api key")
    return x_api_key


@app.get("/private")
def private(_: str = Depends(require_token)):
    return {"ok": True}
```

`Header(default=None)` is the header equivalent of `Query` — it pulls a value out of the request headers rather than the query string, and FastAPI does the name conversion for you, so the parameter `x_api_key` reads the header `X-API-Key`. Underscores become hyphens, and HTTP header names are case-insensitive anyway.

The underscore as a parameter name is a real Python convention meaning "I am obliged to accept this but I don't intend to use it." You want the *check* to run; you don't care about the returned key. You'll write exactly that in the task.

The alternative — an `if` at the top of every single endpoint — is worse in a way that's easy to underrate. It isn't the typing. It's that the day someone adds a fourteenth endpoint and forgets the `if`, nothing tells them. With a dependency, forgetting it means the route has no auth parameter at all, which is visible in the signature. And if you want it everywhere unconditionally:

```python
app = FastAPI(dependencies=[Depends(require_token)])
```

applies it to every route on the app.

### 2.6 The killer feature: overriding dependencies in tests

Everything above is nice. This is the part that actually justifies the machinery.

```python
app.dependency_overrides[get_client] = lambda: FakeClient()
```

`app.dependency_overrides` is a plain dictionary hanging off your app object, mapping a dependency function to something to use *instead*. When FastAPI is about to resolve `Depends(get_client)`, it checks that dictionary first. If there's an entry, it calls that instead and your real `get_client` is never touched.

Look at what that gets you. No monkeypatching — you aren't reaching into another module to rewrite its attributes. No global flag saying "we're in test mode." No conditional inside your production code. Your app doesn't know or care that it's being tested; it just asks for a client and receives whatever the current wiring provides. And because the override is keyed on the function object itself, it works no matter how many routes depend on it or how deeply the dependency is nested.

**This is the argument for `Depends` over module-level globals.** Not tidiness, not fashion — it makes the app testable by design. Every seam you put in is a place a test can stand. Go and look at this unit's `test_task.py` next to unit 22's and you'll see the difference immediately: unit 22's fixture reaches in and rewrites your module, while this one just sets a dictionary entry.

**The practitioner's detail, and it will bite you.** `dependency_overrides` is state on the `app` object, and the `app` object outlives any single test. Set an override and forget to remove it and it stays in place for every test that runs afterwards in the same process — including ones that were meant to hit the real thing. So the override always goes in a fixture that cleans up after itself:

```python
app.dependency_overrides.clear()      # always, in the teardown
```

That is precisely what the `upstream` fixture in this unit's `test_task.py` does: it installs the fake, yields to the test, and clears on the way out. Read it before you start the task, because it also shows you the exact shape the fake client has to have.

---

## 3. Central error handling, and getting HTTP out of your service layer

### 3.1 `HTTPException`, briefly

You met this in unit 20. Raising it anywhere in a handler stops the handler and produces a JSON error response:

```python
raise HTTPException(status_code=404, detail="user not found")
```

which sends `{"detail": "user not found"}` with status 404. Two things about it you may not have needed yet. It takes a `headers=` argument, so you can attach something like `Retry-After` to a 429. And `detail` doesn't have to be a string — it can be any JSON-serialisable value, which lets you send structured errors that a client can actually branch on:

```python
raise HTTPException(status_code=400, detail={"field": "limit", "problem": "must be <= 100"})
```

Worth doing when a machine is going to read the error. A human-readable sentence is fine when a human is.

### 3.2 The actual problem: your service layer should not know what HTTP is

Here's the term, since I'm going to lean on it. Your **service layer** is the part of your program that does the real work — fetching, computing, reshaping — as opposed to the part that deals with the web. In `task.py` the service layer is `fetch` and `slim_repo`. The web part is the endpoints, the dependencies, and the handlers.

In unit 22 those two got mixed. `upstream_error` lived down among the fetching code and it returned an object with a *status code* in it. So the function that talks to GitHub had an opinion about HTTP responses going out to your callers.

Ask yourself what happens the day somebody wants to run that same fetching logic from a command-line script, or from a background worker that writes to a database, or from a test. None of those have callers. None of them have status codes. A 502 means nothing to a cron job. The HTTP-ness has been baked into a place where it doesn't belong, and you can't get it out without rewriting.

### 3.3 The fix: a domain exception plus one handler

Split it in two. The service layer raises an exception that describes *what went wrong in its own terms* — a **domain exception**, one you define yourself to talk about your problem rather than about the transport:

```python
class UpstreamError(Exception):
    def __init__(self, kind, context=""):
        super().__init__(f"{kind}: {context}")
        self.kind = kind
        self.context = context
```

The `kind` is a short string like `"not_found"` or `"timeout"`. It says what happened. It says nothing about what status code anyone should see, because the service layer has no business having an opinion about that.

Then, at the edge of the application, one **exception handler** — a function you register with FastAPI that says "whenever this exception escapes a handler anywhere, here's the response to send instead":

```python
@app.exception_handler(UpstreamError)
async def handle_upstream(request, exc: UpstreamError):
    return JSONResponse(
        status_code=503,
        content={"detail": f"upstream failed: {exc.context}", "kind": exc.kind},
    )
```

The decorator registers it. The function takes the request and the exception that was raised, and returns a `JSONResponse` — the object you build when you want to control the status code and body directly rather than letting FastAPI infer them from a return value.

Now trace a failure through the whole system. `fetch` gets a 404 from GitHub and raises `UpstreamError("not_found", context="ghost")`. It has no idea what happens next. The exception propagates up out of your endpoint. FastAPI catches it, finds the registered handler, and the handler decides: 404, with this body. The mapping from domain to HTTP lives in exactly one function, and it is the only function in the entire program that knows both vocabularies.

The mental model: **the exception handler is the border post.** Inside the border, everyone speaks your domain's language — kinds and contexts and what actually went wrong. Outside, everyone speaks HTTP. One place does the translation, and it's the only place that needs a dictionary for both languages.

This is a thread that's been running since unit 08. There you learned to *catch* exceptions that other people's code raised at you. Here you're on the other side of it: you're *designing* which exceptions exist, what they carry, and who is allowed to interpret them. That's the difference between using a language and defining one.

**The practitioner's detail.** When you raise your domain exception from inside an `except` block, write `raise UpstreamError("timeout", context=ctx) from exc`. The `from exc` records the original exception as the cause, so the traceback in your logs shows both — your `UpstreamError` *and* the `httpx.TimeoutException` underneath it, with the real line number. Without it you get your own exception and no trace of what actually happened at the socket, which is the difference between a two-minute diagnosis and an hour of guessing.

### 3.4 The catch-all handler

Register one more, for everything you didn't anticipate:

```python
@app.exception_handler(Exception)
async def handle_unexpected(request, exc):
    logger.exception("unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "internal error"})
```

This exists so that a bug in your code produces a bland 500 rather than a stack trace in the response body. Stack traces leak file paths, library versions, and sometimes variable contents, and they're a genuine security finding in a review.

The `logger.exception(...)` line is not optional and I'd rather over-stress it than under-stress it. A catch-all that returns a friendly message and doesn't record what happened builds a system that fails *invisibly* — everything looks fine on the dashboard, users get 500s, and there is no evidence anywhere of what went wrong. Catching an error and discarding it is worse than not catching it.

---

## 4. Choosing the status code

This is the table. The right-hand column is what you type; the left is when.

| Situation | Status |
|-----------|--------|
| Bad input FastAPI can't catch declaratively | 400 |
| Missing or invalid credentials | 401 |
| Credentials fine, but you're not allowed | 403 |
| The thing doesn't exist | 404 |
| Conflicts with existing state | 409 |
| Failed a constraint you declared | **422 — automatic, you write nothing** |
| Caller went over a rate limit | 429 |
| Something broke on your side | 500 |
| Upstream returned garbage | 502 |
| Upstream timed out | 504 |

The 422 row is the one people forget they get for free. Every `Query(ge=1, le=100)` and every Pydantic model from unit 21 produces a 422 with a detailed body, automatically, before your function is entered. You never write it. Several tests in this unit assert on exactly that, and if you find yourself hand-writing validation to produce one, you've missed something.

Two pairs are worth real attention, because they're the ones that get asked about.

**401 versus 403.** 401 means *we do not know who you are* — no credentials, or credentials that didn't check out. 403 means *we know exactly who you are and you may not do this.* Different fixes: a 401 says "log in," a 403 says "ask for access." The reason everyone muddles them is that the HTTP spec named 401 "Unauthorized" when it means unauthenticated, and named 403 "Forbidden" when *that's* the one about authorization. That naming mistake has been baked into the specification since RFC 2068 in 1997 and it is never going to be fixed. Learn the meanings and ignore the names. If you say this out loud in an interview it lands well, because it's the kind of thing you only know from having been confused by it.

**500 versus 502.** 500 is *my bug*. 502 is *somebody else's service misbehaved and I'm the messenger*. The distinction matters operationally rather than pedantically: 500s page you, and 502s page whoever runs the upstream. A gateway that reports every upstream failure as 500 has made its own error rate unreadable, and you'll spend on-call hours chasing bugs that aren't yours. In this unit's task, GitHub returning a 500 to you becomes a 502 going out, and that's precisely why.

Then 504 and 503 fill out the picture. 504 means "they didn't answer in time" and 503 means "I couldn't reach them at all" — a DNS failure, a refused connection. Both are retryable by the caller in a way a 502 usually isn't, which is the real information you're transmitting.

The mental model for the whole table: **a status code answers two questions for a machine — whose fault is this, and is it worth trying again?** Everything else is detail in the body.

---

## 5. Testing your app

### 5.1 `TestClient`

```python
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

The important word is **in-process**. `TestClient` does not start a server, does not bind a port, and does not send anything over the network. It calls your application object directly, in the same Python process as the test, handing it a request and taking back a response. The interface it gives you is deliberately identical to the `requests`/`httpx` calls you've been making since unit 12 — `.get()`, `.status_code`, `.json()` — so there's no new API to learn, only a new thing to point it at.

Being in-process buys you three things. Tests run in milliseconds, so you can run them on every save. There's no port to conflict with, no server to start and stop, and no race between "server booting" and "test running." And — this is the one that surprises people — it works on `async` endpoints with no async test setup whatsoever. Your endpoints in `task.py` are all `async def`, your test functions are all plain `def`, and it just works, because `TestClient` runs the event loop for you internally.

Everything you'd expect is there:

```python
client.get("/items", params={"limit": 5})
client.post("/items", json={"name": "x"})
client.patch("/items/1", json={"stars": 2})
client.delete("/items/1")
client.get("/private", headers={"X-API-Key": "secret"})
```

Mental model: **a test is your app's second caller.** You've been the first one all along, poking `/docs` in a browser. The test is the same act, written down so it can be repeated by someone who isn't you.

### 5.2 What to test, honestly

In an interview you will not have time to write a suite, and nobody expects one. What they're reading is whether you know *which* tests are worth the minutes. Two or three good ones signal more than a dozen trivial ones — and a dozen trivial ones actively signal the wrong thing, because they read as someone chasing a coverage number.

The three that earn their keep:

1. **The happy path.** A normal request comes back with the right status and the right shape. This proves the thing works at all.
2. **The error path.** A missing resource gives a 404, not a 500. This is the one that separates people, because it proves you thought about failure before it happened rather than after.
3. **Validation.** A bad parameter gives a 422. Cheap to write, and it demonstrates you know the framework is doing that work for you.

And keep your pure logic in plain functions so it can be tested with no HTTP involved at all. `slim_repo` in this task takes a dict and returns a dict — no client, no request, no app. Its tests are two lines each. That's unit 06's fetch/transform split earning out one last time: the transform half is always the easiest thing in the codebase to test, and every function you can move to that side is a function you can check for free.

### 5.3 Fixtures, and why `autouse` matters

A **fixture** is pytest's word for setup that runs around a test. You write a function, decorate it with `@pytest.fixture`, and a test that names it as a parameter receives whatever it provides. If the fixture uses `yield` instead of `return`, everything after the `yield` runs as teardown — the same before-and-after shape as a generator dependency, which is not a coincidence; both are built on the same Python feature.

```python
@pytest.fixture(autouse=True)
def clean_state():
    reset_store()
    yield
    reset_store()
```

`autouse=True` means every test in the file gets it whether or not it asks. That's the right setting for anything that resets shared state, because the failure mode of forgetting is genuinely nasty.

Here's what happens without it. Test A sets `app.dependency_overrides[get_client]` and doesn't clear it. Test B runs afterwards and silently uses A's fake. Now B passes — for the wrong reason, or fails for a reason that has nothing to do with what it's testing. Run B on its own and it behaves differently. **Tests that pass alone and fail together are the worst kind of flakiness**, because the failure depends on *ordering*, so it appears and disappears when you add an unrelated test, and it will not reproduce when you try to debug it in isolation. An `autouse` cleanup fixture costs four lines and removes the entire category.

---

## 6. Middleware, worth sixty seconds

**Middleware** is code that wraps every request on its way in and every response on its way out — outside your handlers, outside your dependencies, outside everything.

```python
@app.middleware("http")
async def add_timing(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.perf_counter() - started:.4f}"
    return response
```

The shape is always this. You get the `request` and a function `call_next`. Anything before `await call_next(request)` happens on the way in; `call_next` runs the rest of the application and hands you back the response; anything after happens on the way out. You must return the response, or nothing reaches the caller.

Middleware is where logging, request IDs, CORS, and timing live. The one detail worth knowing: because it sits outside everything, it runs on responses your endpoints never produced — 404s for routes that don't exist, and the output of your exception handlers. So the timing header in the task shows up on error responses too, which is exactly what you want when you're trying to find out whether a 504 took ten seconds or ten milliseconds.

`time.perf_counter()` rather than `time.time()`, incidentally, because `perf_counter` is a monotonic clock built for measuring intervals and can't jump backwards when the system clock is adjusted.

A timing header is also, frankly, a cheap and visible touch in a demo. It takes five lines and the person watching can see it in their browser's network tab. Small things that make a service look finished are worth their cost.

---

## 7. Look these up yourself

Reading documentation under mild pressure remains the most transferable skill in this course, so as always, a short list I've deliberately left for you:

- `fastapi.Cookie` — the same idea as `Header`, for cookies.
- `Depends` on a class with a `__call__` method, which is how you build a dependency that takes configuration.
- `RequestValidationError` — how to customise the body of that automatic 422.
- `fastapi.middleware.cors.CORSMiddleware` — you'll need it the first time a browser front-end calls your API.
- `TestClient` used as a context manager (`with TestClient(app) as c:`), which is what makes `lifespan` startup and shutdown events actually run during tests.
- `pytest.raises` with `HTTPException`, for testing a dependency directly rather than through a route.

---

## 8. Check yourself

1. When do you return 502 rather than 500?
2. What does a dependency that `yield`s give you that one that `return`s doesn't?
3. How do you replace a dependency in a test, and what must you do afterwards?
4. Why does `TestClient` not need a running server?
5. What does `autouse=True` do on a fixture, and what does it prevent?
6. Why shouldn't the service layer raise `HTTPException` directly?
7. Which three tests earn the most credit per line?

*(Answers: 1. when the failure came from an upstream service rather than your own code — the distinction decides who gets paged. 2. guaranteed cleanup after the response has been produced, like a `with` block stretched across the request. 3. `app.dependency_overrides[dep] = fake`, and you must clear the dictionary in teardown or it leaks into every later test in the process. 4. it calls the ASGI application object in-process rather than sending bytes over a socket. 5. applies it to every test in the file without their asking, which prevents shared state leaking between tests and producing order-dependent failures. 6. because a status code is meaningless to a CLI, a worker, or a test — keeping HTTP at the edge is what lets the same service code be driven by any of them. 7. happy path, error path, validation.)*

---

*Three ideas to carry into the capstones. A dependency is a seam — a declared place where your app says "something goes here," which is simultaneously what gives you guaranteed cleanup, single-source-of-truth parameters, and enforceable auth, and what makes the whole thing testable without a single monkeypatch. A domain exception plus one central handler keeps HTTP at the edge of your program, so the code that does the actual work could just as easily be driven by a worker or a script; unit 22 did that translation inline, and moving it outward is the whole upgrade. And two or three deliberate tests — happy path, error path, validation — plus an `autouse` fixture that resets shared state, is more convincing than any amount of coverage.*

*Now open [`task.py`](task.py). You are rebuilding unit 22's gateway with all of this in place, and the result is the shape you'd actually write for a service you had to live with. Both capstones start from here.*
