# 13 — Parameters, Headers, Auth, and Sending Data

**Time: ~25 min lesson + ~30 min task.**

*Unit 12 taught you to get data out of one endpoint. That is a big step, but it left you with almost no control: you took whatever that URL happened to hand back. This unit is about controlling the request — narrowing what you ask for, proving who you are, and sending data upward instead of only pulling it down. Read it straight through, then open `task.py`. Everything is defined as it appears, and where it builds on unit 11 or 12 I'll say so rather than repeat those units.*

*Two things to keep in the back of your mind as you read. The interview scenario is that someone hands you a live endpoint and asks you to fetch something specific and say something useful about it — and "something specific" is exactly what this unit's parameters are for. And the target shape, from unit 04, is still a list of flat dictionaries. Nothing has changed about the destination; this unit is about getting better raw material to start from.*

---

## 1. Query parameters, properly

A **query parameter** is a filter you attach to the end of a URL to narrow what the server sends back. You've seen the shape in unit 11: everything after the `?`, written as `name=value` pairs joined by `&`. If SQL is your background, the query string is roughly the `WHERE` clause and the `LIMIT` — it's how you tell the server which slice of its data you actually want, so that it does the filtering rather than you downloading everything and filtering afterwards.

You could build that string by hand. You should not. `requests` takes a dictionary and does it for you:

```python
params = {
    "q": "language:python stars:>1000",
    "sort": "stars",
    "order": "desc",
    "per_page": 50,
}
r = requests.get(url, params=params, timeout=10)
```

Here is the mental model worth carrying: **the params dictionary is a filter form you fill in, and `requests` is the clerk who files it for you.** You write down what you want in plain Python values; the clerk worries about the punctuation, the escaping, and quietly ignores the boxes you left blank.

That clerk does four specific things, and the four are worth knowing individually because two of them are useful and one is a trap.

| Situation | What `requests` does |
|-----------|--------------|
| Value contains a space, `&`, `#`, `:`, `/` | Percent-encodes it correctly |
| Value is `None` | Omits the parameter **entirely** |
| Value is a list | Repeats the key: `{"id": [1, 2]}` becomes `?id=1&id=2` |
| Value is `True` / `False` | Sends the text `True` / `False` — **often wrong** |

Take those in turn. **Percent-encoding** is the escaping scheme from unit 11 — a space becomes `%20`, a colon becomes `%3A` — and it exists because some characters already mean something structural inside a URL. Getting it wrong by hand is easy and produces a request that is silently wrong rather than loudly broken, which is the worst kind of wrong.

The `None` behaviour is the genuinely useful one and it deserves more than a table row. Because a `None` value makes the parameter vanish, you can write **one** params dictionary listing every optional filter you support, and the ones the caller didn't set simply aren't sent:

```python
params = {
    "q": query,
    "since": since or None,        # absent when the caller didn't specify
    "per_page": per_page,
}
```

Compare that with the alternative, which is a stack of `if` statements each adding one key to a dictionary you build up gradually. The single-dictionary version is shorter, and more importantly you can *read* the full set of supported filters at a glance instead of reconstructing it from control flow. This is the pattern the task's `clean_params` function generalises.

The list behaviour is worth knowing mostly so you recognise it when it isn't what you wanted. Repeating a key is one convention for sending multiple values; the other is joining them with commas into a single parameter, and section 8 shows a real API that insists on the second. `requests` does the first automatically, so if the API wants the second you must join the list yourself.

And now the trap. Python's `True` is not JSON's `true` and it is definitely not a URL's `true`. `requests` renders a Python boolean by calling `str()` on it, which gives you the capitalised text `True`, and a great many APIs look at that and either reject it or, worse, fail to recognise it and silently treat the filter as off. **If a boolean filter isn't taking effect, this is why.** The fix is to send the lowercase string `"true"` yourself. The task makes you build that conversion into `clean_params`, because it is the sort of thing you want handled once rather than remembered every time.

One habit to build now, because it costs nothing and saves whole debugging sessions: the first time you call a new endpoint, print the URL that actually went out.

```python
print(r.url)
```

`requests` records the fully assembled URL on the response, so this shows you exactly what went over the wire — encoding, dropped parameters and all. When a request returns something you didn't expect, comparing that line against the API's documentation resolves it faster than any amount of staring at your dictionary.

---

## 2. Reading response headers

Unit 11 introduced **headers** as the metadata attached to a request or response — the envelope rather than the letter. You send some (who you are, what format you'd like) and the server sends some back (what format this actually is, how much quota you have left). Unit 12 had you send a couple. This section is about reading the ones that come back.

They arrive on the response as something that behaves like a dictionary:

```python
r.headers["Content-Type"]
r.headers.get("X-RateLimit-Remaining")   # .get -- it may not be there
```

Use `.get()` for anything optional, for exactly the reason unit 04 gave: square brackets raise and stop your program, and most interesting headers are ones the server *may* send rather than must.

There's a kindness here that will also mislead you once. `r.headers` is **case-insensitive**, so `r.headers["content-type"]` and `r.headers["Content-Type"]` both work. HTTP header names genuinely are case-insensitive by specification, and `requests` gives you an object that honours that. But a plain Python dictionary is not case-insensitive, so the moment you're handed headers as an ordinary `dict` — from a recorded fixture, from a test, from somebody else's code — the kindness evaporates and you have to normalise the keys yourself, usually by lowercasing them.

The practitioner's detail for this section is which headers are worth actually looking at, and the answer is the rate-limit family. A **rate limit** is the cap an API puts on how many requests you may make in a period. Most services tell you where you stand in headers named something like these:

```python
print("remaining:", r.headers.get("X-RateLimit-Remaining"))
print("resets at:", r.headers.get("X-RateLimit-Reset"))
```

Printing those on any long pull turns "the script died after four minutes and I don't know why" into "I had eleven requests left and used them." Unit 15 builds proper handling on top of this — waiting, backing off, retrying — but the reading is a one-liner and you can do it today.

---

## 3. Authentication

**Authentication** is proving to the server that you are someone in particular. The mental model: **it's a badge you show at reception, and it lives in a header on every single request.** HTTP has no memory between requests — unit 11's point that each request stands alone — so there is no "logging in" once. You present the badge every time.

There are four schemes you'll meet, and they differ mostly in what the badge looks like.

### Bearer token — the common case

A **bearer token** is a long random string that stands for "whoever holds this is allowed in." The name is literal: the server doesn't check who you are, only that you bear the token. You put it in the `Authorization` header behind the word `Bearer`:

```python
import os

token = os.environ["GITHUB_TOKEN"]           # KeyError if unset -- deliberate
headers = {"Authorization": f"Bearer {token}"}
r = requests.get(url, headers=headers, timeout=10)
```

That square-bracket lookup is deliberate rather than careless. This is the case unit 04 described as a genuine bug you want to hear about loudly: if the token is missing, nothing downstream will work, and a `KeyError` on line two is far kinder than a confusing 401 on line ninety.

It's also worth doing even when an API works without it. GitHub, for instance, allows sixty unauthenticated requests an hour and five thousand authenticated ones. Same endpoints, same data — the token just moves you into a different tier.

### API key in a header or a query parameter

An **API key** is the same idea with a different name and usually a longer life: a string the service issues you, identifying your account. Some services want it in a header, some in the query string:

```python
headers = {"X-API-Key": key}
# or
params = {"api_key": key}
```

When you have the choice, put it in the header. Query strings get written into server access logs, sit in browser history, and get passed along in the `Referer` header when a page links elsewhere. A header does none of that. Plenty of real APIs only offer the query-string form and you use it anyway — but knowing the difference, and saying it out loud, is a small credibility win.

### Basic auth

**Basic auth** is the oldest scheme: a username and password sent together on every request. `requests` has a dedicated argument for it:

```python
r = requests.get(url, auth=("username", "password"), timeout=10)
```

Under the hood it combines the two, base64-encodes them, and puts the result in the `Authorization` header behind the word `Basic`. Note that base64 is *encoding*, not encryption — anybody who sees the request can decode it trivially. Basic auth is only safe over HTTPS, which is also true of the other schemes but matters most here.

### No auth at all

The fourth scheme, and the one this unit's task actually uses, is nothing. Open-Meteo, Frankfurter and JSONPlaceholder are all open. That's why they're good practice targets: you can concentrate on the shape of the request instead of on getting credentials.

---

## 4. Secrets come from the environment

This is short, and it is the single most quotable thing in the unit.

**Never write a credential into a source file.** Not in an interview, not in a demo, not "just temporarily until it works." Source files get committed, pushed, shared over Slack, pasted into chat windows, and screen-shared. A token in a source file is a token you have published.

The alternative is an **environment variable** — a named value that lives in the operating system's environment for your terminal session or machine, outside your code entirely. Your program reads it by name at run time:

```python
import os

token = os.environ.get("API_TOKEN")
if not token:
    raise RuntimeError("set API_TOKEN in the environment")
```

`os.environ` behaves like a dictionary of every environment variable currently set, so `os.environ["API_TOKEN"]` raises when it's missing and `os.environ.get("API_TOKEN")` returns `None` — the same distinction from unit 04, applied to a different dictionary.

Setting one for the current session, on Windows PowerShell:

```powershell
$env:GITHUB_TOKEN = "ghp_xxx"     # current session only
```

The reason this gets its own section rather than a footnote is the interview. Saying *"I'd read this from an environment variable and never commit it"* takes about three seconds, and it is exactly the sort of thing an interviewer is listening for, because it signals you have handled a credential in anger rather than only in a tutorial. The task's first function, `build_headers`, exists to make you do it once with your hands.

---

## 5. Sending data up: POST

Everything so far has been about *asking*. A **POST** request sends data upward — creating a record, submitting a form, running a search too complex for a query string. Unit 11 covered what the method means; this is how you actually do it.

```python
r = requests.post(url, json={"title": "hello", "body": "world"}, timeout=10)
```

That `json=` argument does three things in one move. It converts your dictionary into JSON text, it puts that text in the **request body** — the payload that travels with the request, as opposed to the URL and headers which are just addressing and metadata — and it sets the `Content-Type` header to `application/json` so the server knows how to read it.

### `json=` versus `data=`

This is the second load-bearing idea of the unit, and the one most likely to cost you time when it bites.

The mental model: **the body is written in some format, and the `Content-Type` header is the label on the parcel saying which format.** Your job when sending is to make the label and the contents agree. `requests` gives you several arguments and each one picks a different format-and-label pair:

| Argument | Body that gets sent | `Content-Type` set |
|----------|-------------|----------------|
| `json={"a": 1}` | `{"a": 1}` | `application/json` |
| `data={"a": 1}` | `a=1` | `application/x-www-form-urlencoded` |
| `data='{"a": 1}'` | the raw string, untouched | none — you must set it yourself |
| `files={"f": open(...)}` | multipart | `multipart/form-data` |

The second row is the one to internalise. **Form-encoded** means the body is written the same way a query string is — `a=1&b=2` — which is what an HTML form submits and what plenty of older services expect. It is a completely legitimate format. It is also completely wrong for a JSON API, and the failure mode is nasty: you get back a 400 or a 422 whose message talks about a missing or malformed field, which sends you hunting through your payload for a typo that isn't there. The payload was fine. The envelope was addressed wrong.

So: **if a POST fails and you don't immediately see why, check `json=` versus `data=` before you check anything else.** It is the classic cause, it takes two seconds to rule out, and ruling it out first will save you more time in this course than any other single habit.

### Reading what came back

```python
r = requests.post(url, json=payload, timeout=10)
print(r.status_code)         # 201 Created, usually
print(r.headers.get("Location"))
created = r.json()
```

A successful creation typically answers `201 Created` rather than `200 OK`, and often includes a `Location` header pointing at the thing it just made. The body is usually the created record, including whatever ID the server assigned — which is normally the piece you actually needed.

And the habit that matters most here: **always print the response body on a 4xx.** A 4xx status tells you the request was your fault, but only the body tells you *how*, and APIs are almost always specific about it — which field, what was wrong with it, what they expected instead.

```python
if not r.ok:
    print(r.status_code, r.text[:500])
```

`r.ok` is `True` for any status below 400. The slice is there because error bodies are occasionally an entire HTML error page, and you want the first useful lines rather than a screenful. This is why the task's `post_json` deliberately does *not* raise on a 4xx: raising throws the explanation away at the exact moment you needed it.

### The other verbs

```python
requests.put(url, json=payload, timeout=10)            # full replace
requests.patch(url, json={"title": "x"}, timeout=10)   # partial update
requests.delete(url, timeout=10)                       # usually returns 204
```

They take the same arguments and behave the same way, so once POST is solid these cost you nothing. There's also `requests.request("GET", url, ...)`, which takes the method as a string — handy when the method is held in a variable rather than typed out.

---

## 6. Practising POST safely

There's an obvious problem with practising requests that create things: you need somewhere to create them, and you'd rather not be writing junk into a real service.

`https://jsonplaceholder.typicode.com` solves this. It accepts POST, PUT, PATCH and DELETE, returns entirely realistic responses, and **stores nothing**. You get a genuine `201`, a genuine body with a genuine assigned ID, genuine headers — and nothing anywhere is modified.

```python
r = requests.post(
    "https://jsonplaceholder.typicode.com/posts",
    json={"title": "hi", "body": "there", "userId": 1},
    timeout=10,
)
r.status_code      # 201
r.json()           # {'title': 'hi', 'body': 'there', 'userId': 1, 'id': 101}
```

Every response is fabricated on the spot, which is exactly what you want while you're learning the mechanics. The task's `create_post` points here.

---

## 7. Time ranges and filter parameters

Analytics-shaped questions almost always come with dates attached, so date parameters are worth a section of their own — and the two APIs in the task happen to demonstrate the two different conventions you'll meet.

First, dates themselves. Nearly every API wants **ISO date** format: `YYYY-MM-DD`, four-digit year, then month, then day, zero-padded, hyphen-separated. `2024-01-07`, never `7/1/24`. When an API rejects a date, the problem is almost always the format rather than the value. There's a bonus to this ordering that section 9 of the task leans on: because the most significant part comes first and every part is fixed-width, ISO date strings sort *chronologically* when sorted as plain text. `sorted()` on a list of them just works, with no date parsing involved. That is not a happy accident — it's why the format was designed that way.

Now the two conventions.

**Comma-joined values in a single parameter.** Open-Meteo wants a list of which measurements you'd like, and it wants them as one parameter with commas inside:

```python
params = {
    "latitude": 52.52,
    "longitude": 13.41,
    "daily": "temperature_2m_max,temperature_2m_min",
    "start_date": "2024-01-01",
    "end_date": "2024-01-07",
    "timezone": "UTC",
}
```

Note that this is *not* what `requests` does with a Python list — a list gets repeated as `daily=a&daily=b`, which this API won't understand. You build the comma form yourself with `",".join(...)`, and the task has `clean_params` do it for you so you only write it once.

**A range encoded in the path.** Frankfurter takes its date range as part of the URL path rather than the query string:

```
https://api.frankfurter.dev/v1/2024-01-01..2024-01-31?base=USD&symbols=EUR,GBP
```

Unit 11 drew the distinction between a **path parameter** — part of the address, identifying *which resource* — and a query parameter, which filters or modifies it. Frankfurter has decided a date range identifies a resource, so it goes in the path and you build it with an f-string. The `base` and `symbols` bits stay in the query where you'd expect. The practical consequence for the task is that you construct the URL and the params dictionary separately, which the tests check explicitly.

There is no rule saying which convention an API will pick. Read the documentation, then print `r.url` and confirm.

---

## 8. Look this up yourself

Reading documentation quickly is the most transferable skill here, so these are deliberately left for you.

- `requests.request(method, url, ...)` — sending a method held in a variable.
- `r.request.headers` — what you actually *sent*, which is the fastest way to debug an auth problem.
- `requests.post(..., data=json.dumps(x), headers={"Content-Type": "application/json"})` — the manual equivalent of `json=`, and why `json=` is better.
- `os.environ` versus `os.getenv` — two ways to the same value, differing in what happens when it's absent.
- `python-dotenv` — loading secrets from a `.env` file so you don't have to set them in every new terminal.
- The HTTP `OPTIONS` method, for asking an endpoint what it permits.

---

## 9. Check yourself

1. What does `requests` do with a parameter whose value is `None`, and why is that useful?
2. Why is an API key in a header better than in the query string?
3. What differs between `json=` and `data=`?
4. Where should a token come from, and what's wrong with the source file?
5. A POST comes back 400. What's the very first thing you print?
6. How do you send a list of values as one comma-joined parameter?

*(Answers: 1. it drops the parameter entirely, which lets you write one dictionary containing every optional filter and let the unset ones vanish, with no conditionals. 2. query strings land in server access logs, browser history, and `Referer` headers; headers don't. 3. `json=` serialises the dictionary to a JSON body and sets `Content-Type: application/json`; `data=` form-encodes it as `a=1&b=2` and labels it as a form. 4. an environment variable — source files get committed, pushed, and shared. 5. `r.text`, because the body is where the API explains what it objected to. 6. `",".join(values)` and send the result as a single parameter — a Python list would be repeated instead.)*

---

*Three things to carry out of this unit. The params dictionary is a form `requests` files for you: it drops `None` values, which is what lets one dictionary express every optional filter without a single `if`, and it renders booleans as capitalised `True`, which is what breaks boolean filters. The body of a POST is written in some format and `Content-Type` is the label saying which, so `json=` versus `data=` is the first thing to check when a POST fails mysteriously. And credentials come from the environment, never from a source file — a sentence worth having ready.*

*The task takes all three and points them at two real endpoints whose responses arrive in awkward shapes: parallel arrays from one, a dictionary keyed by date from the other. Reshaping both into unit 04's list of flat dictionaries is the actual exercise, and it is precisely what you'd be asked to do with a live endpoint under interview conditions.*

*Now open [`task.py`](task.py).*
