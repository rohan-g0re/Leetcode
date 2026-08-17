# The Interview Playbook

*Read after Part 2. Read again the night before. Read §1 and §8 an hour before the call.*

You are handed a URL you have never seen. Maybe with a sentence of context, maybe not.
The clock starts. This document is the procedure.

The single biggest failure mode is **freezing because you don't know the data yet**, and
the fix is mechanical: you have a fixed first five minutes that require no knowledge of
the API whatsoever. Run the procedure and the unknown becomes known.

---

## 1. The first five minutes (do this every single time)

### Step 1 — Say what you're about to do. Out loud.

> "Before I write anything, I want to look at one response and understand its shape.
> Then I'll confirm with you what 'useful' means here, then build."

This buys you thinking time, signals process, and — critically — invites them to correct
your direction *before* you've spent 20 minutes going the wrong way. Interviewers score
this. Silence for four minutes while you read JSON scores badly even if the code ends up
identical.

### Step 2 — Fetch exactly one response and look at it.

```python
import requests, json

r = requests.get(URL, timeout=10)
print(r.status_code)
print(r.headers.get("content-type"))
print(r.text[:1000])
```

Three lines, three facts: did it work, is it JSON, what does it look like. Do not skip
`status_code` — if it's 401 or 403 you have an auth problem, not a data problem, and
those are solved completely differently.

### Step 3 — Determine the top-level shape.

```python
data = r.json()
print(type(data))

if isinstance(data, dict):
    print(list(data.keys()))
elif isinstance(data, list):
    print(len(data), type(data[0]))
    print(json.dumps(data[0], indent=2)[:1500])
```

There are only three realistic answers, and each tells you what to do next:

| Shape | Looks like | What it means |
|-------|-----------|---------------|
| **List of dicts** | `[{...}, {...}]` | Best case. This is already a table. One dict = one row. |
| **Dict wrapping a list** | `{"results": [...], "count": 320, "next": "..."}` | Envelope. The real data is under one key. The others are *pagination metadata* — note them, you'll need them. |
| **Single dict** | `{"name": ..., "stats": {...}}` | One entity. You probably need to fetch many of these, one per ID. |

### Step 4 — Get the field inventory of one record.

```python
record = data[0] if isinstance(data, list) else data
print(json.dumps(record, indent=2))
```

Then out loud, name what you see: which fields are identifiers, which are numeric (can be
aggregated), which are categorical (can be grouped by), which are timestamps (can be
bucketed by time), and which are nested (need flattening). That four-way classification is
the whole of "what analysis is possible here" and doing it aloud makes you look like you've
done this before, because it's exactly what experienced people do.

### Step 5 — Ask your questions.

Three good ones, tailored to what you just saw:

1. "Is there pagination — should I pull all pages or is one page enough for this exercise?"
2. "Am I optimizing for correctness and clarity, or do you want to see me handle scale
   and failure modes too?"
3. "What's the output you want — a printed summary, a saved file, or an endpoint?"

Asking these is not weakness. Shipping the wrong deliverable *is*.

---

## 2. Decide the shape of your answer

Whatever they asked, it's one of four things. Recognize which and you know your skeleton.

| They asked for | You build |
|----------------|-----------|
| "Get X and tell me Y" | Fetch → parse → aggregate → `print` a small summary |
| "Load this into something usable" | Fetch → normalize → DataFrame → clean → save CSV/Parquet |
| "Wrap this / expose this" | FastAPI app with 2–3 endpoints proxying + reshaping upstream |
| "Pull everything" | Paginated fetch loop with rate-limit handling, then one of the above |

**Always write it as functions, never as a top-to-bottom script.** Three functions with
clear boundaries:

```python
def fetch(...) -> dict:      ...   # I/O only. Network in, raw data out.
def transform(raw) -> list:  ...   # Pure. No network. Given data, returns data.
def summarize(rows) -> dict: ...   # Pure. The actual answer.
```

This separation is worth real points on its own. It means `transform` and `summarize` are
testable without a network, it means you can `print` intermediate results while debugging,
and it's the boundary every reviewer looks for. If you take one structural habit from this
course, take this one.

---

## 3. Fetching, defensively

The version you write in the first minute:

```python
r = requests.get(url, timeout=10)
r.raise_for_status()
data = r.json()
```

`timeout=10` is non-negotiable. Without it, `requests` waits **forever** if the server
never responds — your program hangs with no error, in front of an interviewer.
Mentioning this unprompted is a small, cheap credibility win.

`raise_for_status()` turns a 4xx/5xx into an exception instead of silently letting you
call `.json()` on an HTML error page (which produces a confusing `JSONDecodeError` far
from the real cause).

If you need many pages or many IDs, use a `Session` — it reuses the underlying TCP
connection instead of doing a fresh handshake per request, and it holds shared headers:

```python
s = requests.Session()
s.headers.update({"Accept": "application/json", "User-Agent": "interview-demo"})
```

Setting a real `User-Agent` matters in practice — GitHub's API rejects requests without
one, and it's the kind of thing that costs ten confused minutes if you don't know it.

---

## 4. Pagination — the three flavors

If the response has more data than it returned, it will tell you how to get the rest in
one of exactly three ways. Recognize the pattern from the keys.

**A. Offset / page number** — `?page=2` or `?offset=100&limit=50`.
Loop, incrementing, stop when a page comes back empty or shorter than `limit`.

**B. Cursor / token** — response contains `"next_cursor": "abc123"` or `"next": "<url>"`.
Loop, feeding the cursor into the next request, stop when it's `null`/absent. Cursors are
opaque — never try to construct one yourself.

**C. `Link` header** — the response header contains
`<https://api.github.com/...?page=2>; rel="next"`. GitHub does this. Parse out `rel="next"`
and follow it; stop when there's no `next`.

**Always cap the loop.** `max_pages` as a parameter. An unbounded `while True` against a
misread API is how you end up sending 40,000 requests during an interview.

```python
pages = 0
while url and pages < max_pages:
    ...
    pages += 1
```

---

## 5. When it fails

| Status | Meaning | Do this |
|--------|---------|---------|
| 400 | Bad request | Your query params are malformed. Print the response *body* — APIs usually say exactly what's wrong. |
| 401 | Unauthenticated | Missing/bad credentials. Ask what auth they expect. |
| 403 | Forbidden **or rate-limited** | Check headers for `X-RateLimit-Remaining` / `Retry-After`. GitHub returns 403, not 429, for rate limits. |
| 404 | Not found | Usually a wrong path or a bad ID — not necessarily an error in your program, and often a legitimate "this record doesn't exist" you should skip past. |
| 429 | Too many requests | Read `Retry-After`, sleep that long, retry. |
| 5xx | Their fault | Retry with exponential backoff. 2–3 attempts, then give up loudly. |

Backoff is `sleep(2 ** attempt)` — 1s, 2s, 4s. Retry 429 and 5xx. **Never retry a 4xx
other than 429**; the request itself is wrong and repeating it just wastes everyone's time.

Say this out loud when you write it: *"I'm only retrying on 429 and 5xx — retrying a 400
would just fail identically."* It's exactly the distinction people forget.

---

## 6. Analysis, in order of what impresses

Do these in order. Ship the boring one first, then climb.

1. **Counts.** `len(rows)`, how many are missing each field. Always start here — it
   catches "I fetched 30 records but there should be 3000" immediately, and it's the bug
   that silently invalidates everything downstream.
2. **Distribution of one numeric field.** min / max / mean / median. Note that mean and
   median diverging tells you the data is skewed, and say so.
3. **Group and aggregate.** "Average X per category" is the single most common ask.
   `collections.Counter` for pure Python, `df.groupby(...)` for pandas.
4. **Time bucketing.** Per day/month counts. Requires parsing timestamps properly.
5. **Join two sources.** Merge the endpoint with another endpoint or a lookup table.
6. **Note something anomalous.** "These 4 records have a null created_at, I'm excluding
   them and here's the count." Volunteering data-quality observations is what separates a
   junior answer from a senior one, and it costs one sentence.

---

## 7. When the API is down or changed shape

It happens. Do not flail.

1. Say it plainly: *"I'm getting a 503 — that's server-side. Let me confirm it isn't me."*
2. `curl` it or open it in a browser to prove it's not your code.
3. Then: *"I'll work against a saved response so we can keep going, and I'll wire the live
   fetch back in at the end."* Paste one recorded response into a dict literal or a JSON
   file and continue.

Continuing productively past a broken dependency is itself a strong signal. Freezing is not.

---

## 8. Talk track — the sentences that earn points

Memorize the shape of these. They're cheap and they land.

- "Let me look at one response before I write anything."
- "I'm setting a timeout so this can't hang."
- "I'm keeping fetching separate from transforming so the logic is testable without the network."
- "I'm using `.get()` with a default here — this field is absent on some records, and I'd
  rather produce a null than crash on record 700 of 1000."
- "Mean is well above the median, so it's right-skewed — a few big values are pulling it."
- "I'm capping pages so a misunderstanding on my side can't turn into thousands of requests."
- "If I had more time I'd add X." — *always* end with this. Name two or three concrete
  things: caching, retry/backoff, tests, handling the `next` cursor, schema validation.
  It converts what you didn't finish from a gap into a demonstration of judgment.

## 9. Anti-patterns that cost you

- Writing 60 lines before running anything. Run after every few lines. The REPL exists.
- `except:` bare, or `except Exception: pass`. It hides the actual bug and reviewers hate it.
- Hardcoding an index like `data["results"][0]["items"][3]` without checking length.
- Silent `while True` fetch loops.
- Going quiet for minutes at a time. Narrate. Even "I'm not sure yet, thinking about
  whether to group first or filter first" beats silence.
- Reaching for pandas for a 12-row problem. `Counter` and `sorted` are faster to write and
  easier to explain.
- Apologizing repeatedly for not knowing something. Say "I don't know that offhand, I'd
  check the docs — here's how I'd find it," then do that. That answer is nearly as good as
  knowing.

---

## 10. Sixty-second skeleton (type this from memory)

Practice until you can produce this without thinking. It's your opening move for a data
extraction task, and having it ready means your first two minutes are spent on *their*
problem, not on boilerplate.

```python
import requests
from collections import Counter

BASE = "https://api.example.com"


def fetch(path, **params):
    r = requests.get(f"{BASE}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def transform(raw):
    """raw -> list of flat dicts. No network here."""
    return [
        {"id": item.get("id"), "name": item.get("name"), "value": item.get("value", 0)}
        for item in raw
    ]


def summarize(rows):
    values = [r["value"] for r in rows if r["value"] is not None]
    return {
        "count": len(rows),
        "missing_value": sum(1 for r in rows if r["value"] is None),
        "total": sum(values),
        "mean": sum(values) / len(values) if values else None,
        "top_names": Counter(r["name"] for r in rows).most_common(5),
    }


if __name__ == "__main__":
    rows = transform(fetch("/items"))
    for k, v in summarize(rows).items():
        print(f"{k:>15}: {v}")
```
