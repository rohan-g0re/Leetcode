# Unit 22 — hints

*Open this once you have been stuck on one specific thing for about ten minutes — long enough that the hint lands on a real question, not so long that you are demoralised. Each section explains the approach and gives partial scaffolding. None of them hands you a finished function.*

---

### `fetch_json`

This one really is three lines, and they are the three from the lesson:

```python
response = await client.get(url, params=params)
response.raise_for_status()
return response.json()
```

Pass `params` through even when it is `None` — `httpx` treats `None` as "no query parameters", so you do not need an `if` around it.

The `await` is on the `client.get` line only. `raise_for_status()` and `.json()` are ordinary synchronous calls that work on the response you already have in hand; there is no network left to wait for by that point. If you find yourself wanting to `await` them, that is the signal that you are thinking of `await` as "this is async code" rather than as "pause here until the network answers."

---

### `upstream_error`

Structure it as a chain of `isinstance` checks, or as a `try`/`except` around a `raise exc` — either works, and the tests call the function directly with an exception object, so use whichever reads better to you.

Start with `httpx.HTTPStatusError`, because it is the only branch that carries a status code. `exc.response.status_code` gets it. Then handle 404 and 429 as their own cases and let everything else — every other 4xx and every 5xx alike — fall through to the 502.

After that, `httpx.TimeoutException` for the 504. **Then** the generic `httpx.RequestError` for the 502 "upstream unreachable". Getting those two the wrong way round is the mistake to watch for: `TimeoutException` is a subclass of `RequestError`, so a `RequestError` check placed first swallows every timeout and your 504 branch becomes unreachable code that no test can ever reach except the one that is failing.

And `return` the `HTTPException` — do not `raise` it. The endpoints do the raising. If you raise here, the tests that call `upstream_error(...)` and inspect the result will blow up instead of getting an object back.

---

### `get_user`

Read the cache first, and read it defensively, because the entry may not exist:

```python
cached = _CACHE.get(username)
if cached is not None:
    fetched_at, payload = cached
    if time.time() - fetched_at < CACHE_TTL_SECONDS:
        return payload

payload = await fetch_json(client, f"{GITHUB}/users/{username}")
_CACHE[username] = (time.time(), payload)
return payload
```

Two nested checks rather than one, because "there is no entry" and "there is an entry but it is stale" are different situations that happen to lead to the same place. The tuple unpacking on line 3 is unit 03's — one line pulls the timestamp and the payload apart.

Now notice the structure of the second half, because it is the whole reason the "must not cache failures" test passes. The cache write sits on the line *after* the `await`. If `fetch_json` raises — a 404, a timeout, anything — the exception propagates straight out of `get_user` and that line never runs. You did not have to write a single line of error handling to get correct behaviour; you got it by putting the statements in the right order.

---

### `summarize_user`

`.get()` with a default for each field, and mind that the defaults are not all the same:

```python
"followers": user.get("followers") or 0,
"name": user.get("name"),
```

`or 0` rather than `.get("followers", 0)` for the numeric ones, for unit 04's reason: a default only applies when the key is *absent*, and GitHub is perfectly capable of sending the key with `null` in it. `or 0` handles both.

For the year, pull `created_at` out first and only slice it if you actually got something:

```python
created = user.get("created_at")
year = int(created[:4]) if created else None
```

`created[:4]` takes the first four characters, `"2011"`, and `int` turns that string into the number. The `if created` guard is what stops you slicing `None` — which is unit 04's most common crash wearing a different hat.

---

### `get_many_users`

Build a small inner coroutine that wraps one fetch in the semaphore, then hand a batch of those to `gather`:

```python
semaphore = asyncio.Semaphore(concurrency)

async def one(name):
    async with semaphore:
        return await get_user(client, name)

outcomes = await asyncio.gather(*(one(n) for n in usernames), return_exceptions=True)
```

Defining `one` inside `get_many_users` means it can see `client` and `semaphore` without you passing them around — a closure, in the unit 06 sense. The `async with semaphore` takes a ticket on the way in and returns it on the way out even if the body raises, so a failing request never leaks a slot.

Now split the outcomes. `gather` gave them back in the order you passed them, so you can walk them alongside the original names:

```python
for name, outcome in zip(usernames, outcomes):
    if isinstance(outcome, Exception):
        errors.append({"username": name, "error": type(outcome).__name__})
    else:
        results.append(summarize_user(outcome))
```

`type(outcome).__name__` gives the class name as a string — `"HTTPStatusError"` — which is what the test looks for. Not `str(outcome)`, which would give you the message.

Three tests measure three different things here, and each can fail independently. The timing test fails if you awaited inside a loop instead of gathering. The partial-failure test fails if you left off `return_exceptions=True`. And the concurrency test fails if you forgot the semaphore — the fake client tracks its own peak in-flight count, so there is nowhere to hide.

---

### The endpoints, in general

Every async endpoint has the same skeleton:

```python
client = get_client()
try:
    payload = await ...
except httpx.HTTPError as exc:
    raise upstream_error(exc, context=username)
finally:
    await client.aclose()
```

Three things to notice. `httpx.HTTPError` is the common ancestor of `HTTPStatusError` and `RequestError`, so this one `except` catches everything `upstream_error` knows how to translate — no need for a stack of clauses here, since the sorting-out happens inside the helper. `raise upstream_error(...)` reads oddly the first time but is exactly right: the helper *returns* an exception and you raise it. And the `finally` runs whether things went well or badly, so the client is always closed.

Call `get_client()` **inside** the handler rather than once at module level. That is the name the tests monkeypatch, and they patch it after the module has been imported — so a client captured at import time would be the real one and every offline test would try to reach GitHub.

---

### `/health` and `/cache`

Both are plain `def`, because neither touches the network. `/health` returns `len(_CACHE)` as `cached_users`. `/cache` needs the count *before* it clears:

```python
removed = len(_CACHE)
_CACHE.clear()
return {"cleared": removed}
```

Reading the length after the clear would faithfully report zero every time, which is a bug that looks entirely reasonable in the diff.

---

### `/users/{username}/repos`

Declare both constraints on the parameters and let FastAPI enforce them:

```python
limit: int = Query(default=5, ge=1, le=100),
sort: str = Query(default="stars", pattern="^(stars|name)$"),
```

`ge` and `le` are "greater or equal" and "less or equal". The `pattern` is a regular expression pinned at both ends, so it matches the whole string and nothing else. Both produce a 422 automatically, and both show up in `/docs` as documented rules — which an `if` inside the function body never would.

For the fetch, `params={"per_page": 100}` goes to `fetch_json`, which is why that function had to pass params through.

The sorting is unit 07's `key=`, with a two-part key for the stars case:

```python
if sort == "stars":
    items.sort(key=lambda r: (-r["stars"], r["name"]))
else:
    items.sort(key=lambda r: r["name"])
```

Negating the star count turns ascending into descending on that field while leaving the name ascending, so ties fall back to alphabetical order in the same single pass. Then `items[:limit]`, and set `count` to the length of what is left *after* the truncation, not before.

---

### `/compare`

The cleaning is one comprehension:

```python
names = [n.strip() for n in users.split(",") if n.strip()]
```

`split(",")` on `"a,, ,b"` gives four pieces, `strip()` removes surrounding whitespace, and the `if` at the end drops anything that was empty or nothing but spaces. Two names survive.

Then check the size by hand and raise a 400 whose detail contains the number 10, so the caller knows what the limit is:

```python
if not names or len(names) > 10:
    raise HTTPException(status_code=400, detail="give between 1 and 10 usernames")
```

That check has to live here rather than in the signature because `names` did not exist until you computed it — `Query` can only validate the raw string that arrived. It is a small distinction and worth being able to state, because "why is this one validated by hand?" is a fair interview question about your own code.

The rest is assembly. `get_many_users` hands you `(results, errors)`; `requested` is `len(names)`, `found` is `len(results)`, `failed` is `errors`. Sort the summaries by followers descending before returning them — `results.sort(key=lambda u: -u["followers"])` — and `total_followers` is `sum(u["followers"] for u in results)`, over the successes only.
