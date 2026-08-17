# 12 — `requests`: Calling a Real API

*This is the unit the interview is actually about. When someone hands you a live endpoint and says "fetch this, clean it up, tell me something useful," everything you do in the first two minutes comes out of this lesson. Read it straight through — about twenty-five minutes — then open `task.py`, which is another thirty-five. Nothing here assumes anything beyond units 01 to 11.*

*Unit 11 taught you what an HTTP request actually is: a method, a path, a query string, some headers, and a body, sent to a server that sends a response back. This unit is where you stop building that by hand. The `requests` library does every part of it for you, and the whole of this lesson is really about learning where it hid each piece.*

---

## 1. The three lines everything else is built on

Here is a complete, working program that calls a real API on the public internet and prints a number out of the answer.

```python
import requests

response = requests.get("https://api.github.com/users/torvalds", timeout=10)
data = response.json()
print(data["public_repos"])
```

That's it. Line one brings in the tool. Line two sends the GET request unit 11 described and waits for the reply. Line three turns the reply's body — which arrives as a lump of text — into Python dictionaries and lists. Line four reads a field out of the dictionary, exactly as you did in unit 04.

Everything else in Part 2 of this course is refinement of those four lines: what to do when the server is slow, what to do when it says no, how to ask for a filtered subset instead of everything, and how to keep going when one record in five hundred is malformed. But the skeleton never changes, and if you can type those lines from memory you already have a working answer to most of what you'll be asked.

**The mental model for the whole unit:** `requests` is a translator sitting between your Python and unit 11's raw HTTP. You hand it Python things — a string for the URL, a dictionary for the query, a dictionary for the headers — and it hands you back one Python object wrapping the whole reply. You never touch the wire format.

---

## 2. What "importing requests" actually means

That first line deserves a sentence, because the vocabulary matters and nobody defines it.

A **library** (also called a **package**) is somebody else's Python code, written once and published so that everyone else can use it instead of writing it again. `requests` is one of these — it is not part of Python itself, which is why you had to install it during setup with `pip install requests`. The `import requests` line makes its contents available to your file under the name `requests`, and from then on `requests.get(...)` means "the `get` function that lives inside the requests library."

That distinction — installed separately versus built in — is worth keeping straight, because a `ModuleNotFoundError: No module named 'requests'` almost always means you installed it into one Python and are running another. If that happens, `python -m pip install requests` uses the same Python you're running, which sidesteps the whole problem.

`requests` is by a wide margin the most-used HTTP library in Python, and it is the one an interviewer will expect to see. There's a newer alternative called `httpx` with an almost identical API plus asynchronous support, which is unit 22's business. For now, `requests`.

---

## 3. The `Response` object is not your data

This is the idea people get wrong first, so it gets its own section and real weight.

When you call `requests.get(...)`, you do not get the data back. You get a **`Response` object** — a single Python value that wraps the *entire* HTTP response from unit 11: the status line, all the headers, and the body. Your data is somewhere inside it, and you have to ask for it.

Think of the `Response` as **a sealed envelope that has already arrived.** The postmark, the return address, and the weight are all readable from the outside; the letter is inside and you have to open it. Here is everything you can read off it:

```python
r = requests.get(url, timeout=10)

r.status_code      # 200                       int
r.ok               # True when status < 400    bool
r.headers          # case-insensitive dict of response headers
r.text             # body as a decoded str
r.content          # body as raw bytes
r.json()           # body parsed from JSON -> dict or list
r.url              # the FINAL url, after redirects and param encoding
r.elapsed          # timedelta: how long it took
r.history          # list of prior responses if it was redirected
```

Read those against unit 11 and they line up one for one. `r.status_code` is the number from the status line — 200 for fine, 404 for not found, 500 for the server broke. `r.ok` is a convenience: it's `True` whenever the status is below 400, which is a shorter way of saying "nothing went wrong." `r.headers` is a dictionary of the response headers, and you read it with unit 04's `.get()` like any other dictionary — with the pleasant twist that it ignores capitalisation, so `r.headers.get("content-type")` and `r.headers.get("Content-Type")` both work.

Then the body, twice over. `r.text` is the body as text — the literal characters the server sent. `r.content` is the same body as raw bytes, which you want when you're downloading an image or a PDF rather than something readable. And `r.json()` is the body **parsed** into Python. To **parse** something means to read text that follows a known format and build real structured values out of it; here it means reading that JSON text and constructing the actual dictionaries and lists unit 04 taught you to walk around in.

Two of the remaining three are diagnostic. `r.elapsed` tells you how long the round trip took, which is how you find out that an endpoint is the reason your script feels slow. `r.history` matters when the server sends a **redirect** — a response saying "what you asked for lives at this other URL instead," which `requests` follows automatically without telling you. If it did, the responses it passed through on the way are sitting in `r.history`, and an empty `r.history` means you got what you asked for directly.

**The practitioner's detail here is `r.url`,** and it is more useful than it looks. It is not the URL you typed — it is the URL that was actually sent, after `requests` encoded your query parameters and after any redirects were followed. When an endpoint returns results that make no sense, printing `r.url` and reading it character by character is the single fastest diagnostic in this entire course. It is how you catch that you typed `per_page` when the API wanted `perPage`, or that a space in your search term went somewhere unexpected. Get in the habit before you need it.

---

## 4. `.json()` is a method, `.text` is an attribute

Look back at that list and notice that one line has parentheses on it and the others don't. That is not a typo, and the distinction behind it is worth pinning down properly because it produces one of the most baffling error messages a beginner meets.

An **attribute** is a value that already sits on an object. You read it by name and nothing happens beyond the reading — `r.status_code` is just *there*, a number that was set when the response arrived. A **method** is a function that lives on an object, and you have to *call* it with parentheses to make it do its work. `r.json()` is a method, and the work it does is parsing.

That matters practically, because parsing costs real time and `.json()` does it **every single time you call it.** It does not cache the result. If you write `r.json()` in five places in a loop body, you have parsed the same text five times. The fix is a habit, not a technique: parse once, into a variable, and use the variable.

```python
data = r.json()
```

And here is the slip. Because the parentheses are easy to forget, people write:

```python
r.json["login"]
```

That does not call anything. `r.json` without parentheses hands you the method *itself* — the function object, unexecuted, just sitting there — and then you try to index into a function with square brackets. Python replies `'method' object is not subscriptable`, which reads like nonsense until you know what happened. If you ever see that message, the fix is always the same: you forgot the parentheses. (Unit 04 showed you the other subscripting error, `'NoneType' object is not subscriptable`. Same family of message, different missing thing.)

The other thing `.json()` does is fail when the body isn't JSON at all. It **raises** — unit 08's word, meaning it stops normal execution and throws an exception up to whoever called it — a `requests.exceptions.JSONDecodeError`, which is helpfully a kind of `ValueError`, so a plain `except ValueError:` catches it. When it happens, don't guess. Look:

```python
print(r.status_code, r.headers.get("content-type"))
print(r.text[:300])
```

You will almost always find an HTML error page, a login redirect, or a plain-text rate-limit message sitting there in `r.text`, and the reason for your failure will be written on it in English. Two lines beats twenty minutes of theorising.

---

## 5. `timeout` is not optional

If you take one defensive habit out of this lesson, take this one. It is the most important thing on the page.

```python
requests.get(url)                # can hang FOREVER
requests.get(url, timeout=10)    # raises requests.Timeout after 10s
```

A **timeout** is a limit on how long you're willing to wait before giving up. The `requests` library has **no default timeout** — none, not a long one — which means the first of those two lines is a genuine promise to wait indefinitely.

Understand exactly what that failure looks like, because it isn't the failure you're imagining. It is not a crash. A server that refuses your connection outright fails fast and loudly, and that's fine. The dangerous case is a server that *accepts* your connection and then simply goes quiet — it never sends a byte, never closes the socket, never says anything. Your program sits there waiting for a reply that is not coming. No error. No traceback. No output at all. Just a cursor blinking in a terminal in front of an interviewer while you try to explain what your program is doing, and the honest answer is that you don't know and it will never tell you.

Ten seconds of nothing is a fact you can act on. Forever is not. So pass `timeout=` on every single request you write, without exception, forever. It costs eight characters.

It's also one of the cheapest things you can say out loud. "I always pass a timeout — `requests` doesn't have a default and a silent server will hang you" takes four seconds to say and marks you as somebody who has had this happen to them.

One refinement worth knowing: you can split the limit into two by passing a tuple, `timeout=(3, 10)`. That means three seconds to *establish* the connection and ten seconds to *receive* the data once it's established. It's the shape you want when you're happy to wait a while for a big slow response but want to bail immediately if the host is unreachable.

---

## 6. Query parameters — hand over a dictionary, don't build a string

Unit 11 showed you the query string: the part of a URL after the `?`, made of `key=value` pairs joined by `&`, carrying the optional bits of your request. It also showed you percent-encoding — the rule that characters with a special meaning in a URL have to be written as `%` plus a hex code, so a space becomes `%20` and a colon becomes `%3A`. That lesson pays off right here, and the payoff is that you never have to do it yourself.

You pass `requests` a dictionary and it builds the query string for you, correctly:

```python
r = requests.get(
    "https://api.github.com/search/repositories",
    params={"q": "language:python", "sort": "stars", "per_page": 5},
    timeout=10,
)
print(r.url)
# https://api.github.com/search/repositories?q=language%3Apython&sort=stars&per_page=5
```

Look at what happened to that colon in `language:python`. You wrote a normal Python string with a normal colon in it; `requests` turned it into `%3A` on the way out, because a raw colon there would have been read as part of the URL's structure rather than as part of your search term. It also turned the integer `5` into text, because a URL is text and nothing else.

**So never build a query string yourself with an f-string.** It looks like it works — `f"{url}?q={query}"` is fine right up until somebody searches for a term containing a space, an `&`, or a `#`. Then the request you send is not the request you meant, and the server has no way of knowing that, so it doesn't complain. It just answers a different question, and you report the wrong number with total confidence. Handing over a dictionary makes that entire class of bug impossible.

**The detail worth keeping** is what `requests` does with `None`. A parameter whose value is `None` is silently dropped — not sent as the text `"None"`, not sent as an empty value, just left out of the URL entirely. That means an optional filter needs no conditional logic at all:

```python
params = {"q": query, "since": since_date}      # since_date may be None
```

If `since_date` has a value, it's sent. If it's `None` — which, remember from unit 01, is exactly what a missing or null field becomes — the parameter simply doesn't appear. No `if`, no branch, no second version of the dictionary. This is a small thing that keeps real fetch functions clean.

---

## 7. Headers, and why GitHub will otherwise reject you

Headers are the metadata lines from unit 11 that travel alongside your request, saying things like what format you'd prefer back and who you are. In `requests`, they're another dictionary:

```python
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "interview-demo/1.0",
}
r = requests.get(url, headers=HEADERS, timeout=10)
```

`Accept` tells the server which format you want the response in. `User-Agent` identifies the program making the call — browsers put their name and version there, and so should your script.

Here's why that second one is not optional trivia: **GitHub returns 403 Forbidden to any request with no `User-Agent` header at all.** It's in their documentation and it's enforced. Most APIs don't care in the slightest, but the one that does will hand you an access-denied error that has nothing whatsoever to do with access, and you will spend ten confused minutes looking for an authentication problem that doesn't exist. Defining a `HEADERS` constant once at the top of the file and passing it on every call costs nothing and removes the possibility.

---

## 8. When the server says no

Two separate things can go wrong with a request, and they fail in completely different ways.

The first is that the request never completes — the network is down, DNS can't resolve the host, the connection is refused, or your timeout fires. In all those cases `requests` raises an exception and you never get a `Response` at all.

The second is subtler and catches people out: **the request completes perfectly and the answer is bad news.** A 404 or a 500 is a successful HTTP exchange. You asked, the server answered, everything worked. `requests` hands you a `Response` with `status_code` of 404 and does not raise anything, because from its point of view nothing failed. It is not going to decide for you that 404 is a problem.

### `raise_for_status()`

That's what this method is for:

```python
r = requests.get(url, timeout=10)
r.raise_for_status()        # raises requests.HTTPError on 4xx/5xx
data = r.json()
```

`raise_for_status()` looks at the status code, does nothing at all if it's below 400, and raises a `requests.HTTPError` if it isn't. It converts "bad answer" into "exception," which lets you handle both kinds of failure with the same unit 08 machinery.

Call it *before* `.json()`, and here's why the order matters. An error response still has a body. When GitHub 404s you it sends back `{"message": "Not Found"}` — perfectly valid JSON. So without `raise_for_status()`, your `.json()` succeeds, you get a dictionary, and your next line reads `data["login"]` and blows up with a `KeyError` about a field that was never going to be there. You end up debugging the wrong line entirely. Worse, if the error page happens to be HTML rather than JSON, `.json()` fails with a decode error that tells you nothing about the actual cause. Fail early and loudly at the point where the real problem is.

### The exception hierarchy

Unit 08 introduced the idea that Python's exceptions form a family tree, and that catching a parent type catches all of its children. `requests` has its own branch of that tree, and knowing its shape saves you writing four `except` clauses:

```
requests.RequestException          <- catch this to catch everything
├── ConnectionError                <- DNS failure, refused, no network
├── Timeout                        <- exceeded your timeout
├── HTTPError                      <- raised by raise_for_status()
├── TooManyRedirects
└── JSONDecodeError                <- body wasn't JSON
```

Every one of those is a kind of `RequestException`, so a single handler catches all network trouble:

```python
try:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()
except requests.RequestException as exc:
    print(f"request failed: {exc}")
    return None
```

That is the shape to remember. One `try`, three lines inside it, one `except`. You can always narrow it later — catching `requests.Timeout` specifically because you want to retry it, say — but starting broad means nothing gets past you while you're under time pressure. Note that `raise_for_status()`'s `HTTPError` is inside the tree too, so the same handler covers both kinds of failure this section opened with.

### Deciding when *not* to raise

Now the judgment call, and it's the most interesting thing in this unit.

`raise_for_status()` treats every 4xx and 5xx identically, as an error. But a 404 frequently isn't one. When you ask GitHub for `/users/some-name-nobody-took` and it returns 404, the server is not malfunctioning and neither are you. It is answering your question correctly: *that user does not exist.* That's a fact about the world. It's **data**, not a failure — and turning a legitimate answer into an exception means your program crashes on a perfectly normal outcome.

So you check the status yourself before deciding:

```python
r = requests.get(f"{BASE}/users/{name}", timeout=10)
if r.status_code == 404:
    return None            # legitimately absent
r.raise_for_status()       # anything else IS a problem
return r.json()
```

Read the shape of that. You single out the one status code that means something specific to you and translate it into a value your caller can work with — `None`, unit 01's word for "there's nothing here." Everything *else* still goes through `raise_for_status()`, because a 500 or a 403 genuinely is a problem and you want to hear about it.

This is the same judgment call unit 04 asked you to make between `d["key"]` and `d.get("key")`: is absence a bug you want to hear about loudly, or is it ordinary data you should carry forward? Same question, one layer up. And making the distinction *deliberately* — and being able to say why out loud — is a small, real signal of experience, because it's the difference between someone who copied a pattern and someone who thought about what their function should mean. The `get_user` function in this unit's task is exactly this case.

---

## 9. The standard fetch function

Everything above collapses into one small function that you should be able to write without thinking. This is your opening move in an interview: type it in the first minute, then build on top of it.

```python
import requests

BASE = "https://api.github.com"
HEADERS = {"Accept": "application/json", "User-Agent": "interview-demo/1.0"}


def fetch(path, **params):
    """GET {BASE}{path} and return parsed JSON. Raises on HTTP errors."""
    r = requests.get(f"{BASE}{path}", params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


data = fetch("/users/torvalds")
repos = fetch("/users/torvalds/repos", per_page=100, sort="updated")
```

Three lines of body, and every one of them is a decision from this lesson: pass the params as a dictionary rather than a string, always send a timeout, convert bad statuses into exceptions before parsing. Pulling `BASE` and `HEADERS` out into constants means the base URL exists in exactly one place, so pointing the whole thing at a different API is a one-line change.

The `**params` in the signature is unit 06's keyword-argument collection: any extra keyword arguments the caller passes get gathered into a dictionary called `params`, which is precisely the shape `requests` wants. That's what makes the call site read as `fetch("/users/torvalds/repos", per_page=100, sort="updated")` rather than `fetch("/users/torvalds/repos", {"per_page": 100, "sort": "updated"})`. Shorter to type and it documents itself.

Note what this function deliberately does *not* do: it doesn't catch anything. Errors propagate — they travel up to whoever called it — because `fetch` has no idea whether its caller wants to abort, retry, or skip. Deciding that is the caller's job, and unit 08 made the case for pushing error policy up rather than burying it.

---

## 10. The six lines for exploring an unknown response

When an interviewer hands you an endpoint you've never seen, you do not start writing the real code. You find out what you're holding first, and this is the recipe. Memorise the shape of it.

```python
import json

r = requests.get(url, timeout=10)
print(r.status_code, r.headers.get("content-type"))

data = r.json()
print(type(data))

if isinstance(data, list):
    print(len(data))
    print(json.dumps(data[0], indent=2)[:1500])
else:
    print(list(data.keys()))
    print(json.dumps(data, indent=2)[:1500])
```

Walk through what each part buys you. The status and content type together tell you whether the call worked and what the server *claims* it sent. `type(data)` answers unit 04's most important question — is this a dictionary or a list of dictionaries? — which decides the shape of every loop you're about to write.

Then the branch prints a readable sample. `json.dumps(obj, indent=2)` takes a Python object and renders it back into JSON text with line breaks and indentation, which is the difference between a nested response you can actually read and a single 4,000-character line. The `[:1500]` slice keeps it to a screenful. For a list you print the length and one element, because the elements of an API list are essentially always the same shape as each other. For a dictionary you print the top-level keys, which is the field list.

Six lines and an unknown endpoint becomes a known one. Doing this in front of an interviewer reads as competent professional behaviour, not as confusion — nobody expects you to have memorised GitHub's field names.

---

## 11. POST, in one line (unit 13 goes deeper)

Everything so far has been GET, which asks for data. When you need to *send* data, the method is POST, and `requests` gives it the same treatment:

```python
r = requests.post(url, json={"title": "hello"}, timeout=10)
```

The `json=` argument does two jobs at once: it converts your dictionary into JSON text and it sets the `Content-Type: application/json` header so the server knows how to read it. There's a sibling argument, `data=`, which sends the same dictionary form-encoded instead — the older format that HTML forms use. Reaching for the wrong one is a common source of 400 Bad Request responses that look mysterious until you realise the server was expecting a different format entirely. Unit 13 covers this properly.

---

## 12. Being a good citizen, which here is self-interest

A rate limit is a cap on how many requests a server will accept from you in a period, and every real API has one. GitHub's is **60 requests per hour** for unauthenticated calls — that is, calls with no API token attached, which is what everything in this unit is.

Sixty sounds like plenty until you write a loop with a bug in it. Burn through the allowance and every subsequent call returns 403 for the rest of the hour, which could easily be the rest of your interview, and there is nothing you can do about it. So:

- Don't loop over requests without a delay or a hard cap on the count.
- While you're developing, fetch each response once and save it to a file, then work from the file. Your logic doesn't care where the dictionary came from, and you can iterate a hundred times on the transformation for the price of one request. Unit 15 shows a proper caching approach; until then, a saved JSON file is completely sufficient.
- This unit's live tests use about six requests. Run them once, not in a loop.

---

## 13. Look this up yourself

Reading documentation under mild pressure is the most transferable skill in this course, so here are things the task doesn't need but you'll want soon. Find them in the `requests` docs or at the interactive prompt.

- `requests.Session()` — a **session** is a reusable connection with shared headers, so you set your headers once instead of on every call and the underlying TCP connection gets reused across requests, which is measurably faster over many calls. Unit 15.
- `r.raise_for_status()` — read the actual exception message it produces, so you recognise it instantly.
- `allow_redirects=False` — how to stop `requests` following redirects for you, and when you'd want to.
- `r.encoding` — how `requests` guesses the character encoding of a text body, and what to do when it guesses wrong.
- `stream=True` — downloading something too large to hold in memory all at once.
- `httpx` — the near-identical library with async support, arriving in unit 22.

---

## 14. Check yourself

Answer these before opening the task. If one isn't immediate, reread that section — it's cheaper than getting stuck later and not knowing why.

1. What happens if you omit `timeout`?
2. Why pass `params=` a dict instead of building the query string?
3. What does `raise_for_status()` do, and why call it before `.json()`?
4. Which exception class catches every `requests` network failure?
5. When is a 404 *not* an error?
6. How do you see the URL that was actually sent?
7. What error do you get from `r.json["login"]`, and what's wrong?

*(Answers: 1. it can hang forever with no error, no traceback, and no output. 2. `requests` percent-encodes correctly and drops `None` values, so a space or an `&` in your search term can't silently change the request. 3. it raises `HTTPError` on 4xx/5xx, so you don't parse an error page as data and then debug the wrong line. 4. `requests.RequestException` — every other requests exception is a child of it. 5. when it means "that record doesn't exist," which is a legitimate answer rather than a failure. 6. `print(r.url)`. 7. `'method' object is not subscriptable` — you left the parentheses off `.json()`, so you're indexing the method itself rather than its result.)*

---

*Four things to carry out of this lesson. First, `timeout=` on every request, always, because the failure it prevents is silent and total. Second, the `Response` is an envelope and not your data — `.status_code`, `.headers`, and `.url` describe the delivery, `.json()` opens it, and the parentheses on that one are load-bearing. Third, hand `requests` a dictionary of parameters and let it do unit 11's percent-encoding for you, because the f-string version fails silently and only on the inputs you didn't test. And fourth, decide deliberately what counts as an error — `raise_for_status()` for everything that's genuinely wrong, your own status check for the 404 that just means "no such record," which is the same judgment unit 04 asked you to make about a missing key.*

*The target shape hasn't changed since unit 04: a list of flat dictionaries. `requests` gets you the raw JSON, unit 04's `.get()` and `or {}` let you survive its gaps, and unit 08's `try`/`except` keeps one bad response from ending the run. The task ahead puts all three together on live GitHub data — including the pure, network-free functions where the real logic lives.*

*Now open [`task.py`](task.py).*
