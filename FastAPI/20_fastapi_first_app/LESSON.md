# 20 — FastAPI: Your First API

*This is the first lesson of Part 4, and it is the one where the course turns around. For nineteen units you have been the person calling somebody else's service. From here you are the service. Read straight through — about twenty-five minutes — then open `task.py`, which takes about the same again. Every term is defined the first time it appears, including the ones that sound like they ought to be obvious. If a word shows up undefined, that is a mistake in this document, not a gap in you.*

*Two promises from earlier units get paid off here, and I'll flag both when we reach them. Unit 10 told you that type hints do nothing at all in ordinary Python and everything inside FastAPI. Unit 11 taught you status codes as things that arrive. Both of those change shape in this lesson.*

---

## 1. You have just changed sides of the conversation

In unit 11 you learned what an HTTP request is: a block of text your program sends across the network asking for something, and a block of text that comes back. In unit 12 onward you sent those requests for real — you called GitHub, you read the status code, you parsed the JSON, you handled the 404 when a repository wasn't there.

Every one of those was you playing the **client**: the side that asks. Somewhere on the other end there was a **server**: the side that answers. You never had to think about it, because GitHub's server is somebody else's problem.

This unit makes it your problem. You are going to write the program on the other end.

Notice how much of what you already know simply flips over rather than being replaced. Unit 11's status codes were numbers you *received* and had to interpret; in this unit they are numbers you *choose and send*, and choosing the wrong one is now your bug rather than somebody else's. Unit 11's distinction between a path parameter and a query parameter was a rule about how to *build* a URL; here it is a rule about how to *read* one. Unit 04's list of flat dictionaries, which you have been massaging data into since Part 1, turns out to be exactly the shape a handler hands back. You are not learning a new subject. You are reading the same conversation from the opposite chair.

The interview reason for caring is direct. "Wrap this public API in a small service of your own" is a standard take-home and a standard whiteboard question, because it exercises everything at once — calling an upstream, cleaning the data, shaping a response, handling the error cases, and having something a person can actually click on at the end. This unit is the skeleton of that answer.

---

## 2. What FastAPI is, and what a server does that your scripts don't

**FastAPI is a framework.** A **framework** is a library that supplies the parts of a program that are the same in every program of its kind, so that you only write the parts that are specific to yours. Every web service ever written has to read raw bytes off a network socket, work out which chunk of text is the URL and which is the body, decode the query string, convert the pieces into usable values, run some code, turn the result back into text, and write it back down the socket. None of that is your idea. FastAPI does all of it and calls your function in the middle.

So the mental model for this whole lesson: **FastAPI is a switchboard. Requests come in on one side, your ordinary Python functions sit on the other side, and the entire job of the framework is to work out which of your functions a given request belongs to, hand it usable Python values, and turn whatever it returns back into a response.** Your functions stay ordinary functions. They take arguments and return dictionaries. Everything web-shaped happens on the framework's side of the switchboard.

That leaves one thing the framework does not do, and it's the thing that makes this different from every script you have written so far.

Every Python file you have run in this course starts at the top, runs to the bottom, and exits. That is a **script**. A **server** is a program that does not exit. It opens a network port — a numbered door on your machine — and then sits in a loop, forever, waiting for someone to knock. When a request arrives it deals with it, sends the answer, and goes straight back to waiting. It only stops when you kill it.

FastAPI itself does not do that waiting. It only knows how to turn a request into a response. The waiting-on-a-port part is a separate program called a **server** in the narrower sense, and the one everybody uses with FastAPI is **uvicorn**. The two talk to each other through an agreed protocol called **ASGI** — Asynchronous Server Gateway Interface — which is just a written-down agreement about the shape of the Python function the server will call and the shape of the data it will pass in. You will never write ASGI code. The only reason to know the word is that FastAPI's own documentation says "ASGI server" constantly and it is otherwise unexplained jargon.

The division of labour, in one line: **uvicorn owns the port and the loop; FastAPI owns the routing and the conversion; you own the functions.**

---

## 3. The smallest app there is, and how to start it

Here is a complete, working web service. Four lines of actual content.

```python
# main.py
from fastapi import FastAPI

app = FastAPI(title="demo")


@app.get("/health")
def health():
    return {"ok": True}
```

`FastAPI()` builds the application object, and by convention you name it `app`. That object is the switchboard — it holds the list of URLs your service answers and which function handles each. `title` is one of several bits of description it accepts; you'll see where it surfaces in the next section.

Now you start it. Not with `python main.py` — that would run the file top to bottom and exit, having never listened to anything. You start the *server*, and tell it where to find your app:

```powershell
uvicorn main:app --reload
```

That command deserves being taken apart properly, because the colon in the middle confuses everybody once.

- **`uvicorn`** is the program you are running. It is the thing that opens the port and loops forever.
- **`main`** is the **module** — Python's word for one importable `.py` file, named without the `.py`. So this means the file `main.py`, sitting in the directory you ran the command from.
- **`app`** is the name of the *variable inside that file*. Not a keyword, not a magic name — just whatever you called the result of `FastAPI()`. If you had written `service = FastAPI()`, you would run `uvicorn main:service`.
- **`--reload`** tells uvicorn to watch your files and restart itself whenever you save one, so your edits take effect without you stopping and starting it by hand. It is a development convenience and you must not use it in production, where it wastes resources watching for changes that will never come.

Read `main:app` as an address with two halves — *which file, then which variable inside it*. That is the whole syntax, and it is the first thing an interviewer will ask you about this command.

When it starts, uvicorn prints the address it is listening on, normally `http://127.0.0.1:8000`. `127.0.0.1` is your own machine talking to itself — the number is the same on every computer in the world and always means "here." Visit `http://127.0.0.1:8000/health` in a browser and you will get back `{"ok":true}`.

**One practitioner's detail, because it will cost you five minutes otherwise.** `--reload` restarts on *file saves*, not on syntax errors being fixed. If you save a file with a broken line, uvicorn restarts, crashes on import, prints the traceback, and then keeps watching. It looks like the server has died. It hasn't — fix the line, save again, and it comes back on its own. Read the traceback rather than restarting the command.

---

## 4. `/docs` — the reason to be pleased about all of this

Go back to that four-line app and, instead of `/health`, visit this:

```
http://127.0.0.1:8000/docs
```

You did not write that route. You get a full interactive documentation page: every endpoint your service has, listed with its URL, its method, every parameter it accepts, the type of each one, which are required, what the response looks like — and a **Try it out** button that fires a real request from the browser and shows you the real reply.

Where does it come from? From your type hints. FastAPI reads the annotations on your handler functions, works out the shape of every endpoint, and writes a machine-readable description of your whole API in a standard format called **OpenAPI** — an industry-wide JSON schema for describing HTTP services, which you can see raw at `/openapi.json`. The `/docs` page is a browser interface rendered from that description. Both are generated from the same source: the code you were going to write anyway.

The mental model: **`/docs` is a mirror. It shows you your own type hints, reflected back as a web page.** There is no second copy to maintain, which means it cannot drift out of date the way hand-written API documentation always does. Change a parameter's type and the docs change on the next reload.

Take this seriously as an interview asset, because it is genuinely the best thing FastAPI gives you. A `curl` command in a terminal proves your endpoint works, and is forgettable. Sharing your screen, opening `/docs`, and clicking **Try it out** while your interviewer watches the response appear is a different kind of moment — it shows the service, the parameters, the validation rules, and the working result all at once, and you didn't write a line of it. Do that at the end of your task. It is a thirty-second demo that reads as though you spent an hour on presentation.

---

## 5. Anatomy of a route

Back to those four lines, this time looking at what they actually declare.

```python
@app.get("/health")
def health():
    return {"ok": True}
```

A **route** is the pairing of an HTTP method and a URL path — `GET /health` is one route, `POST /health` would be a different one. FastAPI's own documentation calls this a **path operation**, meaning the same thing: an operation (the method) on a path (the URL). The function underneath is the **handler** — the code that runs when a request matches that route. Route, path operation, endpoint, and handler all circle the same idea, and you will hear all four; the only distinction worth holding is that the route is the *address* and the handler is the *code*.

Now the line with the `@` on it, which is the piece you have met only glancingly.

**A decorator is a function that takes the function defined below it and does something with it.** You saw the shape in unit 10 with `@dataclass`, where the tool took your class and wrote extra methods into it. Here the job is different and simpler. `@app.get("/health")` hands your `health` function to the application object and says: *register this function as the handler for `GET /health`*. The app writes it into its routing table. That is the entire effect — a registration, one entry added to a list of "when this URL arrives, call this."

Two consequences worth stating explicitly, because both surprise people.

First, **the function's name is irrelevant to routing.** FastAPI never looks at it when matching a request. Calling it `health`, `health_check`, or `banana` changes nothing about which URL it answers — only the string in the decorator does that. (The name does become the operation's identifier in the OpenAPI document, so a meaningful one still reads better in `/docs`. Just don't imagine it's doing any work.)

Second, **you never call the handler yourself.** You define it and walk away. FastAPI calls it, once per matching request, with arguments it assembled out of the URL. This is the inversion that makes web code feel unfamiliar at first: in a script you decide what runs next, and in a server the incoming request does.

The other methods work identically: `@app.post`, `@app.put`, `@app.patch`, `@app.delete`. Unit 11's verbs, now on the receiving end. This unit's task is read-only and uses nothing but `@app.get`; unit 21 brings in `@app.post` once there is data to send.

**What you return becomes the response.** Return a dictionary and FastAPI converts it to JSON, sets the `Content-Type: application/json` header, and sends it with status 200. Return a list of dictionaries — unit 04's target shape, the one you have been converting messy data into since Part 1 — and it does the same. Numbers, strings, `True`/`False`, `None`, and Pydantic models (unit 21) all work too.

Say that last part out loud once, because it's the thing beginners keep looking for and never find: **you never touch a serializer.** There is no `json.dumps` in a FastAPI handler, no response object to construct, no encoding step. You build the same list of flat dictionaries you would have built for pandas or for a CSV, you `return` it, and it goes out as JSON. Unit 04's advice — *whatever mess arrives, your first transformation is to get to a list of flat dictionaries* — turns out to have been aiming at this the whole time.

---

## 6. Path parameters, and the promise unit 10 made

Most URLs have a variable piece in them. You want `/repos/flask` and `/repos/click` to be handled by one function that receives the name.

You write the variable piece in curly braces in the path, and take a parameter of the same name in the function:

```python
@app.get("/users/{username}")
def get_user(username: str):
    return {"username": username}
```

The name inside the braces and the name of the parameter must match exactly; that matching is how FastAPI knows which parameter to fill from which part of the URL. A parameter filled this way is a **path parameter**, which is unit 11's term arriving from the other direction: there it was the part of the URL that identifies *which specific thing you want*, and it still is.

Now the part this unit exists for.

```python
@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id, "double": item_id * 2}
```

Look at what `item_id: int` does here, and compare it against what the identical annotation does in a plain Python script.

In a plain script it does nothing whatsoever. Unit 10 was blunt about this: write `def f(x: int)`, call `f("hello")`, and Python runs it happily. The annotation is stored on the function for humans and editors to read, and the running program ignores it completely.

Inside FastAPI, that same annotation is enforced:

- A request for `/items/42` arrives, and your function is called with the **integer** `42`. Not the string `"42"` — the conversion already happened. `item_id * 2` gives `84`, not `"4242"`, which is unit 01's `+` trap defused before it reached you.
- A request for `/items/abc` **never reaches your function at all.** FastAPI tries to convert `"abc"` to an integer, fails, and sends back a **422** — the status code meaning "I understood your request, but the contents are invalid" — with a body naming exactly which parameter was wrong, what was expected, and what it received. Your handler is not called. You write no validation and no error message.

That is the payoff unit 10 promised, and it is worth stopping on for a second. The same six characters, `: int`, are pure decoration in one context and a working validator in another. Nothing about the syntax tells you which. The difference is entirely that FastAPI *bothers to read them* — it inspects your function's annotations at import time and builds a parser and a validator out of them. Any library is allowed to do this. Almost none do.

The mental model: **the annotation is the door policy.** It is checked before your function is entered, not inside it. By the time your code is running, the argument is already the right type — which means the defensive type-checking you wrote by hand in units 08 and 14 has no place in a FastAPI handler. It already happened, upstairs, for free.

---

## 7. Route order matters, and here is the mechanism

This is a real bug, one of the tests in this unit's task exists purely to catch it, and it is far easier to avoid once you know *why* it happens rather than just being told the rule.

Suppose you want two routes under `/users`: a specific one for the logged-in user, and a general one that takes a username.

```python
@app.get("/users/me")
def me(): ...

@app.get("/users/{username}")
def get_user(username: str): ...
```

Written in that order, everything works. Written in the other order, `/users/me` is broken — a request for it lands in `get_user` with `username="me"`, and you go looking for a user literally named "me."

The mechanism is worth having in your head. FastAPI keeps its routes in a **list**, in the order the decorators ran, which is the order they appear in your file top to bottom. When a request arrives it walks that list from the start and uses **the first route that matches**. It does not gather all the matches and pick the most specific one; it does not score them; it stops at the first.

So think of your routes as an `if`/`elif` chain rather than a lookup table. `/users/{username}` matches *any* single segment after `/users/`, including the literal text `me`. If it's earlier in the chain, it wins, and everything after it that could also have matched is unreachable.

The rule that falls out: **declare specific literal paths before the patterns that could swallow them.** In this unit's task, `/repos/top` must be declared above `/repos/{name}`, or `{name}` captures `"top"`, your lookup fails to find a repository named "top", and you get a 404 from a route that looked perfectly correct. The test that catches this checks that `/repos/top` returns a list rather than an error — a failure there is never a logic bug in your ranking code, it is always this.

**The practitioner's version of this:** when a route mysteriously 404s or returns the wrong shape, and the handler looks right, check whether an earlier route with a `{parameter}` in the same position is eating it. Open `/docs` and read the endpoints in the order they're listed — that list *is* the matching order, which makes the problem visible in about three seconds.

---

## 8. Query parameters

The other half of unit 11's URL anatomy. Everything after the `?` in a URL — `?q=python&limit=5` — is the **query string**, and each `name=value` pair in it is a **query parameter**. In unit 11 these were the knobs you turned when calling somebody else's API: filters, page sizes, sort orders. Now you are the one offering the knobs.

FastAPI's rule for telling the two kinds apart is beautifully simple and worth memorising, because it is a guaranteed interview question:

> **A function parameter whose name appears inside braces in the route path is a path parameter. Every other parameter is a query parameter.**

That's it. There is no separate declaration.

```python
@app.get("/search")
def search(q: str, limit: int = 10, offset: int = 0):
    return {"q": q, "limit": limit, "offset": offset}
```

None of `q`, `limit`, or `offset` appears in `/search`, so all three come from the query string. A request for `/search?q=python&limit=5` calls your function with `q="python"`, `limit=5` (an integer, converted for you), and `offset=0`.

**Whether a parameter is required is decided by whether it has a default**, using exactly ordinary Python's rules:

- `q: str` — no default, therefore **required**. A request without it gets a 422 saying the field is missing.
- `limit: int = 10` — has a default, therefore optional. Leave it out and your function receives `10`.

To say "optional, and absent means absent," combine unit 10's `X | None` with a default of `None`:

```python
@app.get("/repos")
def repos(language: str | None = None):
    if language is None:
        return {"all": True}
    return {"language": language}
```

`language: str | None = None` reads as "a string or nothing, and nothing is the default." Inside the handler, `None` means the caller didn't ask to filter, which is a genuinely different thing from asking to filter by an empty string. This is unit 01's `is None` discipline arriving in a new place, and this unit's task has a test that punishes getting it wrong: `archived` is `bool | None`, and `archived=False` must mean "only the non-archived ones" rather than "don't filter." A truthiness check treats those two identically. `if archived is not None:` distinguishes them.

Booleans have one pleasant convenience. `archived: bool` accepts `true`, `True`, `1`, `yes`, and `on` from the query string, plus their negatives, because a URL can only carry text and people write it every way imaginable.

---

## 9. `Query(...)` — validation and documentation in one line

A bare `limit: int = 10` gets you type conversion, which stops `limit=abc`. It does nothing about `limit=-1` or `limit=999999`, both of which are perfectly good integers and neither of which you want.

`Query` is how you attach constraints:

```python
from fastapi import Query

@app.get("/search")
def search(
    q: str = Query(min_length=2, max_length=50, description="search term"),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    ...
```

The constraint names are short and come from mathematics: `ge` is greater-than-or-equal, `gt` greater-than, `le` less-than-or-equal, `lt` less-than. For text there are `min_length`, `max_length`, and `pattern` for a regular expression. `default=` is where the default value goes once you're using `Query` — note that `q` above has no `default=`, which keeps it required, exactly as a bare parameter with no default would be.

Anything violating a constraint produces a 422 with a precise message you did not write, naming the parameter, the rule it broke, and the value it received. And the same constraints appear in `/docs`, where the input boxes show the allowed ranges.

That is the idea the framework is built around, and it deserves naming: **declare the rule once, and get parsing, validation, error messages, and documentation out of the single declaration.** Four jobs, one line. Any of them written by hand can drift out of agreement with the others; here they cannot, because there is only one source.

Cash that against something you already built. In unit 08 you wrote `validate_page_size` by hand — check the type, check it's not a boolean, check the range, raise the right exception with a useful message. That was a genuinely instructive exercise and it was also thirty lines. `Query(default=10, ge=1, le=100)` is the same function written declaratively, with a better error message than the one you wrote, and it appears in the documentation as a bonus. This unit's `/search` endpoint makes the point sharply: `q: str = Query(min_length=2, max_length=50)` produces all three of the failure cases the tests check — missing, too short, too long — and you write no validation code at all.

`Path(...)` is the identical tool for path parameters, and takes the same constraints:

```python
from fastapi import Path

@app.get("/items/{item_id}")
def get_item(item_id: int = Path(ge=1)):
    ...
```

**One practitioner's detail worth carrying.** Put your constraints on the *parameters*, not in the body of the handler. It's tempting to accept a bare `int` and check the range yourself on the first line, and it works — but then the rule is invisible in `/docs`, the error message is yours to write and maintain, and a client discovers the limit by being rejected rather than by reading. A constraint declared on the parameter is published; a constraint buried in an `if` is a secret.

---

## 10. Errors: raise, don't return

Sometimes the request is perfectly well-formed and you still can't fulfil it. The repository genuinely isn't there. That's unit 11's 404 — and now you're the one sending it.

```python
from fastapi import HTTPException

@app.get("/users/{username}")
def get_user(username: str):
    user = lookup(username)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user
```

**`HTTPException` is an exception class** — unit 08's machinery, inheriting from `Exception` the way unit 10's section on inheritance described — that FastAPI knows about specially. When one escapes a handler, FastAPI catches it, uses its `status_code` as the response status, and sends a JSON body of `{"detail": <your detail>}`.

**Raise it. Do not return it.** This is the single most common beginner mistake in FastAPI, and it fails in a nasty way: `return HTTPException(404, "nope")` doesn't error, because you have merely constructed an object and handed it back. FastAPI serializes the object into some JSON and sends it with **status 200**. Your caller sees a successful response containing a thing that describes a failure. Nothing warns you. If you're wondering why your 404 test is getting a 200, this is why, every time.

The reason it must be raised is worth a sentence, because it explains the design rather than just the rule: raising unwinds the stack immediately. You can `raise` from six levels deep inside a helper function and the request ends there, with the right status, without every intermediate function having to check a return value and pass a failure upward. It is unit 08's whole argument for exceptions over error return codes, applied to HTTP.

The `detail` string is what your caller reads. Make it name the thing that was missing — this unit's task requires `"repo not found: <name>"`, echoing back what was asked for, because "not found" on its own tells a caller debugging a batch of a thousand requests nothing at all.

You can also set a non-200 status for a *successful* response, on the decorator itself:

```python
@app.post("/items", status_code=201)
def create_item(...): ...
```

201 is unit 11's "Created," and it is the correct status for a POST that made something new. You won't need it in this unit — everything here is a `GET` returning 200 — but it's the natural companion to the 404 above and you will use it in unit 21.

---

## 11. `def` or `async def`?

You will see both in FastAPI examples, often on the same page with no explanation, so here is the honest answer for now.

```python
@app.get("/a")
def sync_handler(): ...

@app.get("/b")
async def async_handler(): ...
```

Both work. Both are correct. FastAPI inspects your function and handles each appropriately: an `async def` handler runs directly on the event loop, and a plain `def` handler is run in a separate thread so that a slow line inside it cannot freeze the whole server while other requests wait.

That last part is the important guarantee, and it's why the boring choice is safe. Because plain `def` handlers get their own thread, calling a blocking library inside one — `requests.get()`, a file read, a database driver that doesn't know about async — is fine. The classic beginner disaster is writing `async def` and then calling `requests.get()` inside it, which *does* freeze the server for every other request, because you promised not to block and then blocked.

**The rule for now: use `def` unless you are `await`ing something.** If there's no `await` in the body, `async` buys you nothing and can only hurt. Unit 22 covers what `await` is and when async genuinely pays — which is specifically when your handler is waiting on several network calls at once. Every handler in this unit's task should be a plain `def`, because none of them wait for anything; the data is already in memory.

---

## 12. Where the files go

For a service this size, **one file is not a compromise, it is the right answer.** A single `main.py` holding the app and its routes is what you should write in an interview, and adding structure to a hundred-line service costs you time and gains you nothing.

```
main.py          # app, routes
```

The convention is worth following, though, because `uvicorn main:app` assumes a file called `main.py` in the directory you're standing in. Name it something else and every command and every tutorial needs adjusting.

When a service outgrows one file, the conventional split is by *kind of thing* rather than by feature:

```
app/
  main.py        # the app object, and route registration
  models.py      # Pydantic models — unit 21
  services.py    # business logic and calls to upstream APIs
  config.py      # settings, URLs, credentials read from the environment
```

The move that makes this work is FastAPI's `APIRouter`, which lets you define routes in one file and attach them to the app in another. Look it up when you need it — for this unit and unit 21 you don't.

---

## 13. Look this up yourself

Reading documentation quickly is the most transferable skill in this course, so a handful of things are deliberately left for you. All of these are one search away in the FastAPI docs.

- `FastAPI(title=..., description=..., version=...)` — where each one appears on the `/docs` page. This unit's `task.py` already sets all three; go and see what they did.
- `@app.get("/x", tags=["reports"])` — groups endpoints into labelled sections in `/docs`. Two seconds of work on a service with seven routes, and it makes the page look deliberate.
- `/redoc` — the second documentation UI, generated from the same OpenAPI document. Nicer to read, no "Try it out" button.
- `uvicorn main:app --host 0.0.0.0 --port 8000` — what `0.0.0.0` means and why the default of `127.0.0.1` means nobody else on the network can reach you.
- `response_model` — the way you declare a response's shape rather than just its contents. That's unit 21.
- `from fastapi.responses import JSONResponse, PlainTextResponse` — for the rare case where you need to control headers or status on a response you're returning normally.
- `fastapi.testclient.TestClient` — read this one before you start, since the tests use it. It calls your app **in-process**: no server running, no port open, no network involved. That is how APIs are tested, and it's why `pytest` works here without you starting uvicorn first.

---

## 14. Check yourself

Answer these before opening the task. If one isn't obvious, rereading its section now is much cheaper than getting stuck later and not knowing which idea is missing.

1. What are the two halves of `uvicorn main:app`, and what does the colon separate?
2. What does `@app.get("/health")` actually *do* to the function below it?
3. How does FastAPI decide whether a parameter is a path parameter or a query parameter?
4. What happens on `GET /items/abc` when the handler declares `item_id: int`?
5. Why must `/users/me` be declared before `/users/{username}`?
6. What status code does a validation failure produce, and who writes the error message?
7. `raise HTTPException` or `return HTTPException` — and what goes wrong if you pick the other one?
8. When should a handler be `async def`?

*(Answers: 1. the module `main.py` and the variable `app` inside it; the colon separates file from variable. 2. registers it in the app's routing table as the handler for `GET /health` — nothing else. 3. any parameter whose name appears in braces in the route path is a path parameter; everything else is a query parameter. 4. an automatic 422 naming the offending parameter, and your handler is never called. 5. routes match in definition order and the first match wins, so `{username}` would capture the literal text "me". 6. 422, and FastAPI writes the message from your type hints and constraints. 7. raise it — returning it produces a 200 whose body merely describes an error. 8. only when there is an `await` in the body; otherwise plain `def`, which FastAPI runs in a thread so blocking calls are safe.)*

---

*Four things to carry out of this lesson. You have swapped chairs: status codes, path parameters, and query parameters are all unit 11's ideas seen from the answering side, and everything you learned about reading them applies to writing them. `uvicorn main:app --reload` is an address with two halves, and the server it starts is a program that never exits — which is the one structural difference between this and every script you have written. The type hint is the door policy: `item_id: int` is decoration in plain Python and a validator here, and that difference is the entire reason unit 10 spent a section on annotations. And a route list is an `if`/`elif` chain matched top to bottom, which is why `/repos/top` has to be declared above `/repos/{name}` and why declaration order is a correctness concern rather than a style one.*

*The task builds a read-only service over the repository fixture: seven routes, filtering, paging, aggregation, search, and one 404. Every handler returns a dictionary or a list of flat dictionaries — unit 04's shape — and you never touch a serializer. When the tests pass, start uvicorn, open `/docs`, and click Try it out on `/repos`. That's the thing worth showing someone.*

*Now open [`task.py`](task.py).*
