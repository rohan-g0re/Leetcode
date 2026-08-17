# 22 — `async`, `httpx`, and Calling Upstream APIs

*This is the lesson where the course turns around on itself. Up to unit 19 you were a client — you called other people's APIs. From unit 20 you have been a server — other people call you. This unit is the first time you are both at once, and the whole lesson is about what changes when your service depends on somebody else's service. Budget about twenty-five minutes to read it and thirty for the task.*

*Fair warning about the vocabulary. Almost every word in this lesson — concurrency, blocking, event loop, coroutine, semaphore, gateway — is genuinely new, not just a technical spelling of something you already do. I define each one the first time it appears and I take my time over it. If a word shows up undefined, that is a bug in this document.*

*One more thing to say up front, because it changes how you should read. This unit contains the single most commonly made mistake in FastAPI, and it is a mistake that takes services down rather than merely making them slow. That is section 3. If you read nothing else properly, read that.*

---

## 1. The interview shape this unit is aimed at

There is a question that comes up constantly in interviews for anything data-adjacent, and it is usually phrased casually: *"here's an API — wrap it, add something useful, and expose it as your own endpoint."*

That is what you are going to build. Your service will sit in front of the GitHub API. Somebody calls *you*; you call GitHub; you reshape what comes back and hand it on. A service in that position has a name — it is a **gateway**. The word just means a service whose job is to stand in front of another service and pass traffic through it, usually adding something on the way: caching, error translation, a friendlier response shape, authentication, rate limiting.

Being a gateway is a genuinely useful thing to be, and it is worth knowing why anyone bothers. Once you sit in the middle, you can cache responses so the upstream service gets asked less. You can fan a single incoming request out into ten upstream ones and combine the answers, which is something no client could do as cheaply. You can hide the upstream's ugliness behind a response shape that fits your own product. And you can translate the upstream's failures into failures that make sense to your callers. Those four things are, in order, sections 10, 6, the task, and section 11 of this lesson.

There is a thread running back through the course here that is worth naming now. In unit 15 you learned about retries, rate limits and caching from the *client* side — you were the one being throttled, the one who had to back off politely. Every one of those concerns comes back in this unit from the other side of the wire, because now somebody is depending on *you*, and your bad behaviour toward GitHub becomes their bad experience of your service. Same problems, opposite chair.

---

## 2. Why `async` exists at all

Start with what a request handler actually spends its time doing, because the answer is what the entire rest of this unit is built on.

Suppose somebody calls your `/users/torvalds` endpoint. Your handler runs, and here is roughly how the time breaks down. Reading the incoming request: microseconds. Building the URL for GitHub: microseconds. **Sending that request over the network and waiting for GitHub to answer: two hundred milliseconds.** Reshaping the JSON that comes back: microseconds. Sending your response: microseconds.

Look at those numbers. Your handler is doing essentially nothing for 99.9% of its life. It is *waiting*.

Now, waiting is not free, and here is why. A running program executes on a **thread**, which is a single line of execution — one sequence of instructions being carried out one after another. A thread can only be in one place at a time. In the ordinary, plain-Python way of doing things, when your handler sends that request to GitHub, the thread *stops there*. It sits on that line of code, doing nothing, for two hundred milliseconds, and it cannot be used for anything else in the meantime. It is like a cashier who scans your card and then stands perfectly still staring at the terminal until the bank replies, rather than starting on the next customer.

If your server has, say, forty threads available, then forty simultaneous requests to a slow upstream will use every one of them, and request forty-one waits in line behind people who are all doing nothing. You have run out of capacity not because you ran out of work-doing power but because you ran out of *waiting* capacity, which is an absurd way to run out of anything.

**Concurrency** is the fix, and the word deserves a careful definition because it is routinely confused with a different one. Concurrency means *making progress on several things over the same period of time by interleaving them*. It does not mean doing several things at literally the same instant — that is **parallelism**, and it needs several processors. A single cashier who starts your card payment, turns to the next customer while the bank thinks, then comes back when the terminal beeps, is concurrent. She is still one person, still doing one thing at a time. She is just never idle.

That cashier is the mental model for this whole unit: **`async` does not make anything faster; it stops one thread from standing still while it waits.** Everything else follows from that sentence. `async` gives you nothing at all on work that is genuinely computing — adding up a million numbers is exactly as slow either way. It gives you enormous wins on work that is waiting, which is nearly all of what a web service does.

### The three words: event loop, coroutine, `await`

Three pieces of machinery make this work, and they are easier than their names suggest.

The **event loop** is a scheduler. It is a single loop, running on a single thread, holding a list of jobs that are in progress. Its entire job is: pick a job that is ready to make progress, run it until it hits a point where it has to wait, park it, and pick another. When something a parked job was waiting for arrives — the network reply comes back — the loop marks that job ready again and resumes it later. It is the cashier's brain. FastAPI starts one of these for you when your app boots; you never create it yourself.

A **coroutine** is a function that can be paused in the middle and resumed later, which is what makes it schedulable. You write one by putting `async` in front of `def`:

```python
async def fetch_user(client, username):
    ...
```

There is a consequence of this that catches everyone once. Calling a coroutine function does not run it. `fetch_user(client, "torvalds")` gives you back a *coroutine object* — a description of some work, not the result of it — and if you print it you get something like `<coroutine object fetch_user at 0x...>`, plus a warning that it was never awaited. It is closer to a recipe than a meal.

**`await`** is how you actually get the meal, and it is the word to spend a moment on because it looks passive and is not. `await something` means: *start this piece of work, and hand control back to the event loop so it can run other jobs, and resume me here with the result when it is done.* Every `await` is a point where your function politely steps aside. That is the whole mechanism. When you see `await` in code, read it as "pause here, others may proceed."

Two mechanical rules fall out of that and they are enforced by Python itself. You can only use `await` inside an `async def` — using it in a plain function is a syntax error. And a coroutine must be awaited by somebody, or its work simply never happens.

Here is the shape you will write a hundred times, with everything defined:

```python
import httpx

@app.get("/users/{username}")
async def read_user(username: str):
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"https://api.github.com/users/{username}")
        response.raise_for_status()
        return response.json()
```

Two things there are new. `async def` on the handler tells FastAPI this is a coroutine and should be run on the event loop. And `async with` is the `with` statement you already know from unit 09's file handling, except that the setup and cleanup steps are themselves things that can be awaited — closing a network client involves I/O, so closing it politely means pausing too.

---

## 3. The rule that actually matters: never block the event loop

This is the most important section in the unit, and the mistake it describes is the number one FastAPI mistake in the wild. I am going to spend a while on it.

A call is **blocking** when it stops the thread it is on until it finishes — no pausing, no stepping aside, nothing else runs on that thread until it returns. Every ordinary Python function is blocking. `requests.get(url)` is blocking. `time.sleep(5)` is blocking. Reading a big CSV with pandas is blocking. There is nothing wrong with any of them; blocking is simply what normal code does.

The problem is what happens when a blocking call goes inside an `async def`.

```python
@app.get("/bad")
async def bad():
    return requests.get(url).json()      # freezes the entire event loop

@app.get("/also-bad")
async def also_bad():
    time.sleep(5)                        # freezes everything for five seconds
```

Remember that the event loop is a single loop on a single thread, and that it can only move on to another job when the current job voluntarily steps aside at an `await`. A blocking call never steps aside. So for the entire two hundred milliseconds that `requests.get` is waiting, **the event loop cannot run anything at all.** Not the other in-flight requests. Not the health check. Not the request that just arrived. Everything in that process is frozen, waiting on a call that has nothing to do with any of it.

Sit with the size of that for a second, because it is what separates this from an ordinary performance mistake. In the `/also-bad` handler, one user hitting one endpoint makes your *entire service* unresponsive for five seconds. Fifty concurrent users of that endpoint and you are down for four minutes. This is not a slowdown, it is an outage, and it is caused by two characters of syntax.

The fix has two halves and you need both.

**Half one: inside `async def`, use only awaitable things.** `httpx.AsyncClient` instead of `requests`. `asyncio.sleep(5)` instead of `time.sleep(5)`. Both of those pause properly, so the loop keeps serving everyone else while your handler waits.

**Half two — and this is the part people miss — a plain `def` handler is completely fine.** FastAPI looks at how you declared your handler. If it is `async def`, FastAPI runs it directly on the event loop, and everything above applies. If it is a plain `def`, FastAPI does something different: it hands your function to a **thread pool**, which is a small standing set of worker threads kept ready for exactly this purpose. Your handler runs on one of those, off the event loop entirely, and if it blocks it blocks only its own worker thread. The loop never notices.

So the honest table is:

| Handler declaration | What belongs inside |
|---------------------|---------------------|
| `def` | `requests`, pandas, a blocking database driver, anything synchronous |
| `async def` | `httpx.AsyncClient`, `asyncio.sleep`, anything you `await` |

Read that table as two valid choices rather than a right one and a wrong one. **`def` plus `requests` is correct and perfectly acceptable code.** It has a ceiling — the thread pool is finite, so it will not scale as far — but it is safe, and for a service handling modest traffic it is entirely reasonable. `async def` plus `httpx` is correct and scales further. What is *not* acceptable is the third combination:

> **`async def` plus a blocking call is a production incident waiting to happen. Mixing them is the mistake.**

Which connects directly back to unit 12. That unit taught you `requests`, and `requests` is a fine library that you should keep using. This unit is the one that tells you where you must *not* use it: never inside an `async def`. That is the entire relationship between the two units, and it is worth having the sentence ready.

The practitioner's detail, and it is the one that makes this real rather than theoretical: **the symptom does not point at the cause.** When someone blocks the loop, what the on-call engineer sees is that unrelated endpoints have gone slow — the health check timing out, a cheap endpoint taking seconds — while the endpoint that actually contains the bug looks fine, because it is doing what it always did. You go hunting through the slow endpoint's code and find nothing, because the culprit is somewhere else entirely. Knowing to ask "is anything blocking the loop?" is what turns a two-day investigation into a two-minute one.

Say that out loud in an interview and you have said something most candidates cannot. It is a strong signal precisely because it is knowledge that only comes from having been burned or having been told carefully.

---

## 4. `httpx` — `requests`, but it can also wait politely

You need a HTTP library that knows how to pause, and that is `httpx`. The good news is that there is almost nothing to learn: `httpx` deliberately copies the `requests` API, so everything you built up over units 12 to 15 transfers directly.

Used synchronously, it is a drop-in replacement:

```python
import httpx

response = httpx.get(url, timeout=10)
response.raise_for_status()
data = response.json()
```

That is unit 12, character for character, with the library name changed. Used asynchronously, the shape is the same with `await` in front of the network call:

```python
async with httpx.AsyncClient(timeout=10) as client:
    response = await client.get(url, params={"q": "python"})
    response.raise_for_status()
    data = response.json()
```

`httpx.AsyncClient` is the async counterpart of `requests.Session`. Like a session, it holds open connections and reuses them across calls, which saves you the several-round-trip cost of establishing a new encrypted connection every single time. And as with a session, you set the timeout and the default headers once on the client rather than repeating them on every call.

Four differences from `requests` are worth memorising, because three of them are names you will need in a `except` clause:

- `httpx.HTTPStatusError` is what `raise_for_status()` raises on a 4xx or 5xx. It replaces `requests.HTTPError`. It carries the response, so `exc.response.status_code` tells you exactly what went wrong.
- `httpx.RequestError` is the base class for everything that went wrong at the network level — DNS failure, connection refused, connection dropped. The response never arrived at all.
- `httpx.TimeoutException` is a *subclass* of `RequestError` for the specific case where you gave up waiting. Remember that word "subclass"; it comes back in section 11 and it is a real trap.
- `httpx.HTTPError` is the common ancestor of both `HTTPStatusError` and `RequestError`, which makes it a convenient single thing to catch when you want to handle every kind of upstream failure in one place.

---

## 5. Fan-out: doing ten things in the time of one

Here is where async stops being defensive hygiene and starts paying you back.

Suppose you want ten GitHub users. The obvious code is a loop:

```python
results = []
for username in usernames:
    response = await client.get(f"{GITHUB}/users/{username}")
    results.append(response.json())
```

That is correct, and it is slow, and the reason is worth being precise about. Each `await` does pause and let the loop serve *other people's* requests — so this is not the disaster of section 3 — but within this handler nothing overlaps. You start request one, wait for it, then start request two. Ten requests at two hundred milliseconds each, one after another, is **two seconds**.

The alternative is to start all ten and then wait for all ten. Sending one request out to many places at once like this is called a **fan-out**, from the picture: one line coming in, ten lines going out.

```python
import asyncio

async def fetch_one(client, username):
    response = await client.get(f"{GITHUB}/users/{username}")
    response.raise_for_status()
    return response.json()

results = await asyncio.gather(*(fetch_one(client, u) for u in usernames))
```

`asyncio.gather` takes any number of coroutines, hands all of them to the event loop at once, and waits until every one has finished. All ten requests are now in flight simultaneously, so the total time is roughly the time of the *slowest single one*: **about two hundred milliseconds**. Same work, same code shape, ten times faster, and the gain grows with the number of calls.

The `*` in front of the parentheses is Python's unpacking operator from unit 06 — `gather` wants the coroutines as separate arguments rather than as one list, and `*` spreads them out.

One property of `gather` matters more than it sounds like it should: **the results come back in the order you passed the coroutines in, not the order they finished.** If user `c` replies first and user `a` replies last, `results[0]` is still `a`'s. That guarantee is what lets you `zip` the results back against the original list of names, which is exactly what the task asks you to do. Without it you would have no way of knowing which answer belonged to which request.

The mental model to keep: **`gather` is "start all of these, and call me when the last one lands."**

### Companion one: `return_exceptions=True`

Now the part that people find out the hard way.

By default, if any single coroutine inside `gather` raises an exception, `gather` immediately raises that exception to you — and **the results of every coroutine that succeeded are thrown away.** Nine of your ten users came back perfectly and you get nothing but the one 404.

For a fan-out, that is almost always the wrong behaviour. You asked about ten users, one of them does not exist, and the useful answer is nine users and a note about the tenth — not a total failure. So:

```python
outcomes = await asyncio.gather(*tasks, return_exceptions=True)
```

With `return_exceptions=True`, an exception is no longer raised — it is handed back to you *as one of the results*, sitting in the list in that coroutine's position. So `outcomes` becomes a mixed list of payloads and exception objects, and you sort them apart yourself:

```python
good = [o for o in outcomes if not isinstance(o, Exception)]
bad = [o for o in outcomes if isinstance(o, Exception)]
```

`isinstance(x, Exception)` asks "is this thing an exception?" — the same tool unit 01 pointed you at for asking "is this an integer?". And because `gather` preserved order, you can pair `outcomes` up with your original list of usernames and know precisely which name each failure belongs to.

Reporting both counts back to your caller — "found 9, failed 1, here is which one" — is the honest answer, and it is a noticeably more mature-looking response shape than either crashing or silently returning nine.

### Companion two: `asyncio.Semaphore`

`gather` is enthusiastic. Hand it three hundred coroutines and it will genuinely try to open three hundred simultaneous connections to GitHub. What happens next is that GitHub rate-limits you, or your operating system runs out of sockets, or someone's firewall decides you are attacking them. This is unit 15's rate limiting arriving from the other direction: there you were being throttled and learning to back off; here you are the one who has to not be rude in the first place.

The tool is a **semaphore**, which despite the intimidating name is just a counter with a cap — think of it as a fixed number of tickets. A coroutine must take a ticket before doing its work and gives it back when it finishes. If no tickets are left, it waits (politely, pausing, letting the loop serve others) until one is returned.

```python
semaphore = asyncio.Semaphore(5)

async def fetch_limited(client, url):
    async with semaphore:
        return await client.get(url)
```

`async with semaphore` takes a ticket on the way in and returns it on the way out, including if the body raises. With `Semaphore(5)`, at most five of these are ever inside that block at once, no matter how many you hand to `gather`. The rest queue up. Your fan-out is still concurrent — it is just concurrent five at a time instead of three hundred at a time.

**Mentioning a concurrency cap without being asked is one of the strongest "I have actually done this" signals available to you in an interview.** Everyone who has read a tutorial knows `gather`. The people who have run a fan-out against a real API in production are the ones who reach for the semaphore in the same breath, because they have been rate-limited before.

---

## 6. Timeouts, and why the stakes went up

Unit 12 told you to always set a timeout, because without one a dead upstream leaves your program hanging forever. That is still true and the syntax is the same:

```python
httpx.AsyncClient(timeout=10)
httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0))
```

The second form splits the budget: at most five seconds to establish the connection, at most ten in total. Useful when a slow-to-connect host and a slow-to-answer host deserve different treatment.

What has changed is the consequence of getting it wrong. In unit 12 a missing timeout hung *your script*, which was annoying and entirely your problem. Now a missing timeout hangs *your service*, and your service has callers, and those callers have their own timeouts and their own callers. A single unresponsive upstream with no timeout on your side propagates outward until everything that depends on you is stuck too. The word for this is a cascading failure, and the timeout is the thing that stops it at your door. A timeout is not a nicety; it is the boundary you draw around somebody else's bad day.

---

## 7. One client, not one per request

Every example so far has created an `AsyncClient` inside the handler. That is fine for learning and fine for the task, but it wastes something real: opening an HTTPS connection costs several network round trips before a single byte of your actual request goes out, and a client that is created and thrown away per request pays that cost every time and gets no benefit from its connection pool.

The fix is to make one client when the application starts up and share it. FastAPI gives you a hook for exactly this, called **`lifespan`** — code that runs once before the first request arrives and once after the last one is served.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(timeout=10)
    yield
    await app.state.client.aclose()

app = FastAPI(lifespan=lifespan)
```

Read it as a sandwich. Everything above the `yield` is startup. The `yield` is "now the application runs, for as long as it runs." Everything below is shutdown. `app.state` is a general-purpose place FastAPI gives you to stash things that should outlive a single request, and `aclose()` is the async close — closing a client politely means waiting for connections to shut down, which is I/O, which is why it needs an `await`.

Reaching into `app.state` from your handlers works but is a bit grubby, and unit 23 shows you the tidy version with `Depends`. For now, know that `lifespan` exists and what it is for; the task uses a simpler arrangement on purpose, for a reason section 9 explains.

---

## 8. Caching: a dictionary and a clock

You are a gateway sitting in front of an upstream with a rate limit. Caching is not an optimisation here, it is the main reason to exist. If a hundred of your users all ask about the same GitHub account within a minute, there is no honest argument for making a hundred calls to GitHub.

To **memoize** a function means to remember the results it has already computed and hand back the stored answer instead of doing the work again. Python has a built-in for it:

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_pure_thing(x): ...
```

And now a thing worth knowing before it wastes your afternoon: **`lru_cache` cannot wrap a coroutine function.** Put it on an `async def` and it will appear to work and then behave insanely. The reason is section 2's point about coroutines: calling a coroutine function returns a coroutine *object*, not a result, so `lru_cache` dutifully caches the object. A coroutine object can only be awaited once. Your first caller awaits it and gets an answer; your second caller gets the same exhausted object back and receives a `RuntimeError: cannot reuse already awaited coroutine`. The cache is technically working perfectly — it is just caching a recipe rather than a meal.

For async, a plain dictionary is completely adequate:

```python
_CACHE: dict[str, dict] = {}

async def get_cached(client, username):
    if username in _CACHE:
        return _CACHE[username]
    data = (await client.get(...)).json()
    _CACHE[username] = data
    return data
```

That version has one flaw: entries live forever, so a user's follower count from three weeks ago is served as current. The fix is a **TTL**, which stands for *time to live* — the maximum age at which a cached entry is still considered good. You implement it by storing the time alongside the value and checking the age when you read:

```python
_CACHE[username] = (time.time(), payload)
```

On the way in, look up the key, and if you find something, subtract its stored timestamp from the current time. Under the TTL, use it. Over the TTL, ignore it and fetch fresh. `time.time()` gives you the current time as a number of seconds, so "how old is this" is plain subtraction. This is exactly the cache the task asks you to build, and the shape is worth having in your fingers.

One detail that is easy to get wrong and that the task tests for: **write to the cache only after a successful fetch.** If you cache the outcome of a request that failed, you have pinned a failure in place for the whole TTL — every caller for the next minute gets the error without you even retrying. Keeping the cache write strictly after the `await` that could have raised gets this right for free, because a raised exception never reaches the next line.

In production you would put this in Redis instead, so that all your server processes share one cache and it survives a restart. In an interview, say that sentence and move on — it shows you know where the toy version stops without derailing into infrastructure.

---

## 9. Translating upstream errors — the section that reads as senior

Your caller should never receive a raw upstream failure. They did not call GitHub; they called you. What they need from you is an answer about *their* request, expressed in terms they can act on.

```python
try:
    response = await client.get(url)
    response.raise_for_status()
except httpx.HTTPStatusError as exc:
    if exc.response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"user not found: {username}")
    raise HTTPException(status_code=502, detail="upstream error")
except httpx.TimeoutException:
    raise HTTPException(status_code=504, detail="upstream timeout")
except httpx.RequestError:
    raise HTTPException(status_code=502, detail="upstream unreachable")
```

The mechanics are unit 08's `try`/`except` and unit 20's `HTTPException`. The interesting part is the mapping, and it is worth understanding rather than memorising, because the reasoning is what an interviewer is listening for. Here is unit 11's status-code vocabulary being *re-emitted*: you receive a status from upstream, decide what it means for your caller, and issue a new one.

**Upstream 404 becomes your 404.** GitHub says the user does not exist; from your caller's point of view the thing they asked for genuinely does not exist. The meaning survives the translation unchanged, so pass it through.

**Upstream 5xx becomes your 502 Bad Gateway.** A 5xx from GitHub means GitHub broke. Your caller's request was perfectly valid and your code did nothing wrong. 502 is the status that means precisely "I am a gateway, and the server behind me gave me a bad response" — it is the one code in the whole list that exists for the situation you are in.

**A timeout becomes 504 Gateway Timeout.** Same family, more specific: the server behind me did not answer in time. The distinction from 502 is worth keeping, because 504 tells whoever is reading your logs that the upstream was *slow* rather than *broken*, and those have different fixes.

**Upstream 429 passes through as 429.** 429 means "too many requests." If GitHub is throttling you, the right move is to propagate that pressure to your callers rather than absorbing it silently and continuing to hammer GitHub on their behalf. This is unit 15's back-off etiquette applied one layer up: you were the one being asked to slow down, and now you are the one asking.

Now the reason all of this matters, which is the practitioner's point of the section. **The default, lazy behaviour is to let everything become a 500, and a 500 means "I am broken."** If you return 500 when GitHub is down, you have filed a bug against yourself. Your caller retries against the same broken thing, your monitoring pages your on-call engineer, and someone spends an hour reading your logs to discover that your code was fine all along. A 502 says, unambiguously and in one number, "not my fault, my dependency is down." The distinction between "I failed" and "my dependency failed" is one of the most useful things a status code can carry, and throwing it away costs real time later.

---

## 10. A note on the task's design, because it looks odd

The task gives you a function called `get_client()` that returns an `httpx.AsyncClient`, and asks that every other function call it rather than making a client of its own. After section 7 you might reasonably ask why it does not just use `lifespan`.

The answer is testing, and it is a lesson in its own right. Because there is exactly one place in the module where a client comes from, the tests can replace that one function with something that returns a *fake* client — an object with a `get` method that hands back canned responses. The word for that swap is monkeypatching, and unit 23 covers it properly. The effect is that your fan-out logic, your cache, your error translation and your endpoints all get tested with no network, in milliseconds, and with total control over what the "upstream" does — including making it time out, or 500, or return a 404 for one name out of two. None of that is possible against the real GitHub.

That is worth generalising: **routing every access to an external dependency through a single named function is what makes a service testable.** If half your functions build their own clients, half your code cannot be tested offline. This is why the task insists on it, and it is a design point worth mentioning if an interviewer asks how you would test a service that calls out.

---

## 11. Look this up yourself

Reading documentation under time pressure is the skill this course cannot hand you. These are all small and all directly useful here:

- `asyncio.wait_for(coro, timeout=5)` — putting a deadline on any coroutine, not just an HTTP call.
- `asyncio.as_completed` — how to process results as they land rather than waiting for the slowest.
- `httpx.Limits(max_connections=...)` — the connection-pool-level version of a semaphore.
- `anyio.to_thread.run_sync` — the escape hatch for calling one unavoidable blocking function from inside an `async def`.
- `asyncio.TaskGroup` (Python 3.11+) — the modern alternative to `gather`, and what it does differently on failure.
- What `httpx.Response.is_success` gives you, and when it is nicer than `raise_for_status`.

---

## 12. Check yourself

1. What exactly happens if you call `requests.get` inside an `async def` handler, and why is the symptom hard to trace?
2. When is a plain `def` handler the right choice?
3. What does `asyncio.gather` guarantee about the order of its results, and what does that let you do?
4. Why would you pass `return_exceptions=True`?
5. What is a semaphore for, and what goes wrong without one?
6. Which status do you return when the upstream returns 500? When it times out? Why not 500 in both cases?
7. Why can't `lru_cache` wrap an `async def`?

*(Answers: 1. it freezes the single-threaded event loop, so every other request in the process stalls; the symptom is that unrelated endpoints go slow while the guilty one looks fine. 2. whenever the handler does blocking work — FastAPI runs `def` handlers in a thread pool where blocking is safe. 3. results come back in argument order rather than completion order, which lets you zip them back against the inputs to know which result belongs to which request. 4. so that one failure does not discard every successful result in the fan-out. 5. it caps how many requests are in flight at once, so you do not get rate-limited, blocked, or run out of sockets. 6. 502 for an upstream 5xx and 504 for a timeout; a 500 claims that you are broken when your dependency is the thing that failed. 7. calling a coroutine function returns a coroutine object rather than a result, so the cache stores an object that can only be awaited once.)*

---

*Four things to carry out of this unit. `async` buys you nothing on computation and everything on waiting, because it stops one thread standing idle while a network call is in flight — that is the whole idea, and every piece of syntax here serves it. Never put a blocking call inside an `async def`; a plain `def` handler with `requests` in it is correct, an `async def` handler with `requests` in it is an outage, and the mistake is mixing them. A fan-out means `gather`, and `gather` in real life always comes with `return_exceptions=True` so one failure does not discard nine successes, and a `Semaphore` so you do not get yourself blocked. And when you sit between a caller and an upstream, translating the upstream's failures into honest statuses — 502 for their 5xx, 504 for a timeout, 429 passed through — is the difference between telling your caller the truth and telling them you are broken.*

*`task.py` builds all of that as one service: a cache with a TTL, a concurrent fan-out with a cap, an error translator, and five endpoints that use them. Unit 23 then takes the client out of the handler and does it properly with dependency injection, and shows you how the tests you have been passing were built.*

*Now open [`task.py`](task.py).*
