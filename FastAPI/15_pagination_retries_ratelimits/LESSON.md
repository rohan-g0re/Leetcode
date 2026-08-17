# 15 — Pagination, Retries, Rate Limits, Caching

*This lesson takes about thirty minutes to read and the task about thirty-five to do. It assumes units 11 and 12 — you know what a status code is and you have used `requests` to fetch one URL — and nothing more. Every term is defined the first time it appears, including the ones that sound like you should already know them. If a word goes by undefined, that's a fault in this document.*

*This is the unit where your code stops being a demonstration and starts being something you'd actually run. Everything before it fetched data. This one fetches data that doesn't fit, from a server that sometimes fails, through a gate that counts how often you knock.*

---

## 1. Why there is a whole unit about fetching

In unit 12 you called an API and got a page of results back. That worked because the example was small. The moment the answer is bigger than one response, three things go wrong at once, and this unit is those three things.

The first is that the data arrives in slices. An API is not going to hand you forty thousand records in a single reply — it would be slow to build, slow to send, and expensive to hold in memory on both ends. So it hands you a hundred, and tells you, in one of three different ways, how to ask for the next hundred. Getting all of it back means writing a loop. That loop is **pagination**.

The second is that the network is unreliable in a way that has nothing to do with your code being wrong. A request times out. A server has a bad minute and returns a 503. A DNS lookup fails. None of these mean "your program is broken"; they mean "try that again." Handling them is **retries**.

The third is that the service is counting. Almost every public API caps how many requests you may make in a window of time, and going over the cap gets you blocked — sometimes for an hour. Living within that budget is **rate limiting**, and the best way to spend less of it is to not make the request at all, which is **caching**.

You have already written the skeleton of the first one. Unit 05's `collect_pages` was exactly this loop — ask for page one, collect, ask for page two, stop when a page comes back empty or when you hit a safety cap — with the network faked out by a function handed in as an argument. That was deliberate. You learned the shape of the loop somewhere it couldn't hurt you. This unit connects the same shape to a real socket, and everything new in it is about what happens when the thing on the other end is real: it fails, it counts, it takes a second per call.

If you get asked to pull data from a live endpoint in an interview — which is the occasion this whole course is aimed at — the code in this unit is the difference between an answer that works on the example and an answer that works.

---

## 2. Sessions, and why you should stop calling `requests.get`

**What it is.** In unit 12 you fetched things like this:

```python
import requests

r = requests.get(url, params=params, timeout=10)
```

That's fine for one request. For a loop, you want a **session** instead. A session is an object that holds settings and a live connection on your behalf, and you make your requests through it rather than through the `requests` module directly:

```python
session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "User-Agent": "interview-demo/1.0",
})

r = session.get(url, params=params, timeout=10)
```

Notice the shape of it. You configure once, then call `session.get` wherever you'd have called `requests.get`. The arguments are identical.

**Why it's worth the two extra lines.** There are two reasons, and one of them is much better than the other.

The good one is **connection reuse**. Before your computer can send an HTTPS request it has to do real setup work: open a **TCP connection** to the server (a negotiated two-way channel, which takes a round trip to establish), and then perform a **TLS handshake** — the exchange where both sides agree on encryption keys so the traffic can't be read in transit. That handshake takes another two round trips and some cryptography. On a connection to a server across an ocean, all of that can cost more time than the actual request does.

`requests.get` throws that connection away after every call and builds a new one next time. A `Session` keeps it open and sends the next request down the pipe that's already there. Over fifty requests in a loop — which is exactly what a paginated pull is — this is routinely two to three times faster, and you changed nothing about your logic to get it.

The second reason is ordinary convenience: headers, authentication, and cookies set on the session apply to every request made through it, so you set your `User-Agent` once instead of remembering it in nine places.

**The mental model:** `requests.get` is knocking on the door, being let in, doing your business and leaving, every single time. A `Session` is being let in once and staying in the room.

**The practitioner's note.** Use a session any time you'll make more than about three requests, and say why out loud if someone is watching: "I'm using a session so the connection gets reused across pages rather than re-doing the TLS handshake each time." It costs you six words and it signals that you have written this code before rather than looked it up. It is also the reason your task's first function is `make_session` and every other function takes a session as its first argument — the session is the thing that carries all the shared setup around.

---

## 3. Pagination: the three styles, and how to tell which one you're looking at

Every API that returns more data than fits in one response has to answer one question: *how do I tell the client where to continue from?* There are three answers in common use. They are not variations on a theme you can guess between — they look different, they loop differently, and they end differently. Your first job on an unfamiliar endpoint is to work out which of the three you've got, and that takes about ten seconds once you know what to look for.

Here is the recognition table. Read it now and come back to it when you're staring at a real response.

| Style | How you recognise it | How you know you're done |
| --- | --- | --- |
| Page / offset | Numbers in the query string: `?page=2`, or `?offset=200&limit=100` | An empty page, or a page shorter than you asked for |
| Cursor / token | A field in the response *body* holding a meaningless-looking string: `"next_cursor": "eyJpZCI6MTAwfQ"` | That field is missing, empty, or `null` |
| `Link` header | Nothing in the body at all — a `Link` header in the *response headers* containing `rel="next"` | There is no `rel="next"` in the header |

Now each one properly.

### 3a. Page and offset numbers

This is the one that looks like SQL, and if you've written `LIMIT 100 OFFSET 200` you already understand it. The client says which slice it wants, by number:

```
?page=2&per_page=100
?offset=200&limit=100
```

The loop is a counting loop. You ask for page one, then page two, and so on:

```python
def fetch_all_pages(session, url, per_page=100, max_pages=10):
    records = []
    for page in range(1, max_pages + 1):
        r = session.get(url, params={"page": page, "per_page": per_page}, timeout=10)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        records.extend(batch)
        if len(batch) < per_page:
            break
    return records
```

Two things in there deserve a sentence each. `records.extend(batch)` rather than `.append(batch)` is unit 03's distinction doing real work: you want one flat list of records at the end, not a list of pages. And there are *two* ways out of that loop, which is not redundancy.

An **empty page** — the server has nothing left — always ends it. But so does a **short page**: if you asked for a hundred and got seven, there is no page after this one, because a server that had more would have filled the page. Checking for the short page saves you an entire extra request, and when each request costs a second of waiting and one unit out of a small hourly quota, that request is worth saving. This is a small optimisation with a good story attached, and stories like that are what interviews are made of.

The trap in this style is that the counting is not standardised. Most APIs start at page 1. Some start at page 0. Your task has both — `paginate_offset` starts at 1 and `paginate_hn` starts at 0 — precisely so you feel the difference rather than assume it.

### 3b. Cursors

The second style hands you a token in the response body and asks you to send it back:

```json
{"results": [...], "next_cursor": "eyJpZCI6MTAwfQ"}
```

That string is a **cursor**: a marker meaning "you got up to here." The loop sends no page number at all. It sends nothing on the first request, then whatever cursor came back on each subsequent one, and stops when no cursor comes back:

```python
cursor = None
for _ in range(max_pages):
    params = {"limit": 100}
    if cursor:
        params["cursor"] = cursor
    data = session.get(url, params=params, timeout=10).json()
    records.extend(data["results"])
    cursor = data.get("next_cursor")
    if not cursor:
        break
```

**The single most important thing about a cursor is that it is opaque.** "Opaque" means you cannot see through it — the value is meaningful to the server and meaningless to you, deliberately. That string above happens to be base64 that decodes to `{"id":100}`, and knowing that is a trap, not a shortcut. The server is free to change what it encodes, add a signature, or encrypt it entirely, without warning, because nobody promised you anything about its contents. **You pass back exactly the bytes you were given and you never, ever construct one yourself.** Code that decodes a cursor and increments the number inside works beautifully right up until the API changes format, at which point it breaks silently rather than loudly.

Why do APIs bother, when page numbers are simpler? Because page numbers are wrong when the data is moving. If you're reading page 3 of a list sorted newest-first and someone inserts ten new records, everything shifts down by ten and you'll see ten records twice while missing ten others. A cursor says "continue after record 4192," which stays correct no matter what got inserted. This is why every large modern API — Stripe, Slack, Twitter — uses cursors, and it's a good answer to give if anyone asks you why.

**The mental model:** a page number is a seat number in a theatre that people keep entering and leaving. A cursor is a bookmark physically stuck in the book.

### 3c. The `Link` header

The third style puts the next URL in the response headers, and GitHub is the API you'll meet it on:

```
Link: <https://api.github.com/user/repos?page=2>; rel="next", <...?page=50>; rel="last"
```

That's a comma-separated list of URLs in angle brackets, each tagged with a **relation** — `rel="next"`, `rel="last"`, sometimes `rel="prev"` and `rel="first"` — saying what that URL is relative to the one you just fetched. You parsed this header by hand in unit 11's task. The good news is that in real code you never have to again, because `requests` parses it for you into a dictionary called `response.links`:

```python
url = start_url
for _ in range(max_pages):
    r = session.get(url, timeout=10)
    records.extend(r.json())
    url = r.links.get("next", {}).get("url")
    if not url:
        break
```

The `.get("next", {}).get("url")` chain is unit 04's `or {}` pattern in its other form: ask for the `next` link, get an empty dictionary if there isn't one, then ask *that* for its URL and get `None` rather than a crash. When `url` comes back `None`, there is no next page and the loop ends.

Now the detail that will actually bite you, and that your task tests explicitly. **The URL you get out of the `Link` header is absolute and already contains the full query string.** Look at it — `?page=2` is right there in it. So on every request after the first, you must send *no params at all*. If you keep passing your original `params={"per_page": 5}` along, `requests` will merge them into a URL that already has its own query, and you can end up requesting a different page from the one the server told you to, which in the worst case means fetching page 2 forever. The fix is one line and it is easy to forget: after the first hop, set your params to `None`.

**The mental model for all three at once:** page numbers are you telling the server where to go; a cursor is the server telling you where you got to; a `Link` header is the server just handing you the next door.

### 3d. Cap the loop. Always. This is not a nicety.

Every example above has a `max_pages`, and I want to be direct about why, because it is the highest-consequence line in this lesson.

A pagination loop makes real network requests, and its exit condition depends on you correctly interpreting a response from a server you did not write. If you misread it — you check `nbPages` when the field is actually `nb_pages`, or you follow a `next` link that points back at page one — the loop does not crash. It does not warn you. It keeps going, at maybe five requests a second, for as long as your program runs. That is thousands of real requests against somebody else's service, from your IP address, in a couple of minutes.

The realistic consequence is not a bill. It's that the API blocks you, and if this is happening during an interview it blocks you *in the middle of the question*, with the interviewer watching, and there is no recovering from that in the time you have.

So the cap is not defensive politeness, it's the brake. Even if your logic is perfect it costs nothing; the moment your logic isn't, it's the only thing between you and a ban. Write it first, before the loop body, every time.

And say it out loud, in these words or your own:

> *"I'm capping this at ten pages so a misunderstanding on my side can't turn into thousands of requests."*

That sentence tells an interviewer, in fifteen words, that you have run code against a live API before and that you think about blast radius. It is one of the cheapest points available in the entire course.

---

## 4. Retries: which failures deserve a second chance

Some requests fail because something went briefly wrong between two computers. Some fail because your request was wrong. Retrying the first kind is how you survive a flaky network; retrying the second kind wastes everyone's time three times as fast and gets you no closer to an answer. So the whole of retry logic is one question — **is this failure the kind that might succeed next time?** — and unit 11's status-code table is where you look up the answer.

| What happened | Retry? | Why |
| --- | --- | --- |
| `requests.Timeout`, `requests.ConnectionError` | Yes | Nothing arrived at all. Genuinely transient. |
| Status 5xx (500, 502, 503) | Yes | Their server broke. Yours is fine. |
| Status 429 (Too Many Requests) | Yes, **but only after waiting** | You went too fast. Slowing down fixes it. |
| Any other 4xx (400, 401, 403, 404, 422) | **No** | The request itself is wrong. It'll be just as wrong in two seconds. |

The bottom row is the one people get wrong. A 404 means the thing isn't there. A 401 means your credentials are bad. Sending the identical request again cannot change either fact — you'll get the same answer, having burned two more units of your rate limit to confirm something you already knew.

**There is a second question hiding behind the first, and it's the one that separates people who have run this in production.** Retrying assumes the request is safe to repeat. Unit 11's methods table is where this comes from: a `GET` is **idempotent** — doing it twice has the same effect as doing it once, because it only reads. A `POST` usually isn't. If your `POST` times out, you genuinely do not know whether the server received it and the reply got lost, or whether it never arrived. Retrying might create a second order, a second user, a second payment. Everything in this unit retries `GET` requests only, and that's not an accident. If you find yourself wanting to retry a `POST`, the real answer is an **idempotency key** — a unique ID you generate and send with the request so the server can recognise a duplicate and ignore it — which is worth knowing the name of even though you won't implement it here.

### Exponential backoff

When you do retry, *when* matters. The naive version waits a fixed second between attempts. The right version doubles the wait each time: one second, then two, then four. That's **exponential backoff**, and in code it's just `base ** attempt` — `2 ** 0` is 1, `2 ** 1` is 2, `2 ** 2` is 4.

The reasoning is worth having straight, because it's the answer to "why not just wait a second each time?" A 503 usually means the server is overloaded. If everyone who gets one hammers back a second later, the server gets the same flood it just failed under, plus the original traffic, and it never recovers. Doubling means each successive attempt is gentler than the last, so the load you're contributing drops off quickly and the server gets breathing room to actually come back. You are not just waiting — you are backing off, which is a different thing and the reason for the name.

Here's the whole retry loop, and it is the shape you should be able to reproduce from memory:

```python
import time

def fetch_with_retry(session, url, params=None, attempts=3):
    for attempt in range(attempts):
        try:
            r = session.get(url, params=params, timeout=10)
        except (requests.Timeout, requests.ConnectionError):
            if attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt)
            continue

        if r.status_code == 429 or r.status_code >= 500:
            if attempt == attempts - 1:
                r.raise_for_status()
            time.sleep(retry_delay(r, attempt))
            continue

        r.raise_for_status()
        return r.json()
```

Read it as three paths out of each attempt. The `try`/`except` catches the case where nothing came back at all — that's unit 08's exception handling, and it is what makes retries possible in the first place, because without it a timeout would simply end your program. The middle block handles a response that arrived carrying a retryable status. And the last two lines handle everything else: `raise_for_status()` turns any remaining 4xx into an exception immediately, with no retry, and if the status was fine you parse the JSON and you're done.

Notice what happens on the *final* attempt in both retryable paths: it re-raises rather than sleeping. There is no point waiting four seconds when you have already decided not to try again. That detail is small and the tests in your task check it precisely.

### Obey `Retry-After` when you're given it

Sometimes the server tells you exactly how long to wait, in a header:

```
Retry-After: 30
```

When it does, use its number rather than your formula. It knows when its quota window resets and you're guessing.

```python
def retry_delay(response, attempt):
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        try:
            return int(retry_after)
        except ValueError:
            pass
    return 2 ** attempt
```

The `try`/`except` around `int()` is there because the specification allows `Retry-After` to hold either a number of seconds *or* an HTTP-format date like `Wed, 21 Oct 2015 07:28:00 GMT`. Parsing the date form is more trouble than it's worth here, so when the value won't convert you quietly fall back to your own backoff. That's a design decision worth recognising: an unparseable header should degrade to a sensible default, never crash the fetch.

### Jitter

One more refinement, worth exactly one sentence in an interview and no more.

If a thousand clients all get a 503 at the same instant and all back off on the same schedule, they all retry at second one together, and again at second two together. The server gets hit by synchronised waves instead of a smooth trickle, which is nearly as bad as no backoff at all. That pattern has a name — the **thundering herd** — and the fix is to blur everyone's timing slightly by adding a small random amount to each wait:

```python
import random
time.sleep((2 ** attempt) + random.uniform(0, 1))
```

That random extra fraction of a second is **jitter**. It costs one line, it desynchronises the herd, and mentioning it tells someone you've thought past the happy path into what happens when your client is one of many.

---

## 5. Rate limits: reading the meter instead of hitting the wall

A **rate limit** is a cap on how many requests you may make in a window of time. The polite APIs tell you where you stand on every single response, in headers:

```python
remaining = r.headers.get("X-RateLimit-Remaining")   # how many requests you have left
reset = r.headers.get("X-RateLimit-Reset")           # when the window refills
```

That `reset` value is a **Unix timestamp** — a count of seconds since the first of January 1970, which is how computers pass absolute times around without arguing about time zones. `1700000000` is a real moment in November 2023. To turn it into something readable you'd use `datetime.fromtimestamp`.

The habit worth building is to read `X-RateLimit-Remaining` *while you loop*, not after you get blocked. Being blocked is a failure you cannot undo; noticing you're nearly out is a decision you can make calmly:

```python
if remaining is not None and int(remaining) < 5:
    print("running low on quota; stopping early with partial data")
    break
```

Stopping early with two hundred records and saying so is a completely respectable outcome. Getting banned mid-demo is not. That is why your task has a `should_stop_for_rate_limit` function and why `paginate_offset` calls it every page.

The other defence is to slow yourself down before anyone asks. A bare `time.sleep(0.2)` between requests in a loop caps you at five per second, which is enough to keep almost any API from noticing you and cheap enough that you won't feel it on ten pages.

**The GitHub trap, which is worth knowing specifically because GitHub is what you'll be handed.** Unauthenticated requests to the GitHub API are limited to **sixty per hour**. Sixty. That is low enough that a couple of enthusiastic pagination loops can exhaust it before you've finished reading the question. With a token it goes to five thousand an hour, which is effectively unlimited for anything you'll do in an interview — so if you have a token, use it. And when you do run out, GitHub does not send you a 429. It sends a **403 Forbidden**, which by the table in section 4 is a status you must never retry. So a rate-limit block on GitHub looks exactly like a permissions error, and your retry logic will correctly refuse to retry it while you sit there wondering why your credentials broke. The way to tell the difference is to read the body, which says something about rate limits, or the `X-RateLimit-Remaining` header, which will say `0`.

---

## 6. Caching: the highest-value habit in this unit

Here's the situation you will actually be in. You're writing a script against a live API. You run it, and something's wrong with your grouping logic. You fix it and run again. Now the field name is wrong. Run again. Now you want the average instead of the sum. Run again. Over twenty minutes you will run that script twenty times, and every single run will fetch the identical data over the network — twenty times the waiting, twenty times the quota, for one dataset that hasn't changed.

There is no reason for that, and fixing it is about eight lines. **Caching** means keeping the response the first time you get it and reading it off disk on every run after. Your loop goes from three seconds to instant, and your quota stops draining while you debug.

The awkward part is naming the file. You need a filename that's unique to this particular request — this URL with these parameters — and that is safe to put on a filesystem, which rules out using the URL itself, since it's full of slashes and question marks. The tool for that is a **hash**: a function that takes any text and produces a fixed-length string of hex digits from it, such that the same input always gives the same output and two different inputs practically never collide. `hashlib.sha256` is the standard one.

```python
import hashlib
import json
from pathlib import Path

CACHE = Path(".cache")

def cache_key(url, params):
    raw = url + json.dumps(params or {}, sort_keys=True)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

**Look hard at `sort_keys=True`, because it is the whole trick and it is easy to leave out.** `json.dumps` turns a dictionary into text, and by default it writes the keys in whatever order they happen to sit in the dictionary. So `{"a": 1, "b": 2}` becomes `'{"a": 1, "b": 2}'` while `{"b": 2, "a": 1}` becomes `'{"b": 2, "a": 1}'` — different text, therefore a different hash, therefore a different filename, therefore a cache miss. But those are *the same request*. Sorting the keys before serialising forces both dictionaries to the same text and the same key, so identical requests hit the cache no matter what order you happened to build the params in. Without that one argument the cache still works, but only sometimes, in a way you'd never think to look for.

The fetch itself is then a check, a fallback, and a write:

```python
def cached_get(session, url, params=None):
    path = CACHE / f"{cache_key(url, params)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    data = fetch_with_retry(session, url, params)
    CACHE.mkdir(exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")
    return data
```

**The mental model:** the cache is a receipt drawer. Before you go to the shop, you check whether you already have the receipt for exactly this purchase.

There's a second, smaller kind of caching worth knowing the name of. **Memoizing** a function means remembering what it returned for each set of arguments so that calling it again with the same arguments returns the stored answer instead of recomputing. Python has it built in:

```python
from functools import lru_cache

@lru_cache(maxsize=256)
def get_user(login):
    ...
```

Two limits on it. The arguments have to be hashable, which — from unit 03 — rules out dictionaries and lists, so you can't memoize a function that takes a params dict. And it lives in memory only, so it vanishes when your program exits. That's the crucial difference: `lru_cache` speeds up repeated calls *within one run*, while the file cache survives between runs, and surviving between runs is the thing that helps while you're iterating.

One honest limitation of the file cache as written: it never expires. Cached data is frozen at the moment you first fetched it, which is exactly what you want for an hour of debugging and exactly wrong for anything long-lived. Real caches attach a **TTL** — *time to live*, a duration after which an entry counts as stale and gets re-fetched. You'd implement it by storing the fetch time alongside the data and comparing against it on read. You don't need it for this task; you do need to know the term, because "how do you invalidate that cache?" is a natural follow-up question and "I'd put a TTL on the entries" is the natural answer.

Finally: **say this one unprompted.** "I'd cache these responses locally so I'm not re-fetching the same data every time I re-run while iterating." It is one of the highest-value sentences in the whole playbook, because it shows you're thinking about the other side of the connection and about your own iteration speed at the same time.

---

## 7. Concurrency, in preview only

Fetching a hundred URLs one after another is slow, and it's worth understanding *why* it's slow: almost none of that time is your computer working. It's your computer waiting for a reply. A hundred requests at 300 milliseconds each is thirty seconds, of which maybe half a second is actual computation.

Since it's waiting rather than working, you can overlap the waits. `concurrent.futures.ThreadPoolExecutor` runs your requests on several threads at once; `asyncio` with `httpx` achieves the same overlap in a single thread, and that's unit 22.

But both collide head-on with section 5. Twenty parallel workers against GitHub's sixty-an-hour unauthenticated budget will exhaust it in a few seconds and leave you blocked for the rest of the hour. If you reach for concurrency you must also add a limit on how many run at once and a delay between them. Correct and slow beats fast and banned, and in an interview, saying exactly that is a better answer than actually writing the thread pool.

---

## 8. Look these up yourself

Reading documentation quickly under mild time pressure is the most transferable skill in this course, so here are the things I've deliberately not explained. Ten minutes total.

- `requests.adapters.HTTPAdapter` together with `urllib3.util.Retry` — retries configured on the session itself, so you never write the loop from section 4 by hand. Worth seeing after you've written it once.
- `response.links` — poke at a real GitHub response in the interactive prompt and print it.
- `requests_cache` — a library that turns section 6 into two lines.
- `time.monotonic()` versus `time.time()` — and why you measure elapsed time with the first one.
- `concurrent.futures.ThreadPoolExecutor` — skim only.
- `hashlib.sha256` — what a hex digest actually is.

---

## 9. Check yourself

Answer these before you open the task. If one isn't immediate, reread the section rather than getting stuck later and not knowing why.

1. What are the two benefits of a `Session`, and which one is about speed?
2. What are the three pagination styles, and where do you look to recognise each?
3. Which failures do you retry, and which do you never retry?
4. Why exponential backoff rather than a fixed wait, and what does jitter add on top?
5. Which status code does GitHub use when you've exhausted your rate limit, and why is that awkward?
6. Why must every pagination loop have a hard cap?
7. Why does `cache_key` pass `sort_keys=True` to `json.dumps`?

*(Answers: 1. connection reuse — no repeated TCP and TLS handshakes — and shared headers and auth; the first is the speed one. 2. page or offset numbers in the query string; a cursor token in the response body; a `Link` header with `rel="next"` in the response headers. 3. retry timeouts, connection errors, 429 and any 5xx; never retry any other 4xx, because the request itself is wrong. 4. doubling the wait reduces the load you add to a struggling server instead of piling on; jitter stops many clients from retrying in synchronised waves. 5. 403, which is a status you'd otherwise never retry and which looks identical to a permissions problem. 6. because a misread stop condition otherwise becomes thousands of real requests and a ban. 7. so that two dictionaries with the same contents in different insertion orders serialise to the same text and therefore the same cache key.)*

---

*Three things to carry out of this unit. First, pagination is one loop with three dialects, and the ten seconds you spend identifying which dialect you're looking at saves you from writing the wrong loop entirely — cursors are opaque and get passed back untouched, and a `Link` header's URL is absolute so you must stop sending your own params after the first hop. Second, retrying is a judgment about the failure and not a reflex: transient failures and 5xx and 429 get another go with an exponentially growing wait, everything else in the 4xx range gets raised immediately, and the whole mechanism only exists because unit 08 taught you to catch an exception instead of dying on it. Third — and this is the one that actually changes how your day goes — cap every loop and cache every response, because those two habits are what stand between a working script and an IP address that GitHub has stopped talking to.*

*Now open [`task.py`](task.py). Ten functions, and by the end of them you'll have a fetcher that pages three different ways, retries intelligently, watches its own quota, and never asks twice for something it already has.*
