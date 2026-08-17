# 11 — HTTP Fundamentals

*This is the only unit in the whole course that never touches the network. Nothing here makes a single call to a single server. That is deliberate, and it is worth twenty minutes of your time before you type `import requests` in unit 12, for one reason: from here on, the library does all of this for you, invisibly and correctly. Which is wonderful right up until the moment something breaks — and then you are staring at an error message about a layer you have never looked at. Everything in this lesson is a thing `requests` will handle on your behalf. You are learning it now so that when it goes wrong you know which piece broke.*

*Read it straight through. Nothing is assumed beyond units 01 to 10, and every term is defined the first time it appears — including the ones that sound like they ought to be obvious.*

---

## 1. What "calling an API" actually is

Let's start with the thing you have been told to do in an interview: *"here's an endpoint, fetch the data."* Underneath every friendly one-line version of that, exactly one thing happens. Your program opens a connection to another computer, sends it a block of text, and gets a block of text back. That is the whole of HTTP. The block you send is called a **request**. The block that comes back is called a **response**.

**HTTP** itself — HyperText Transfer Protocol — is just the agreed-upon rules for what those two blocks of text look like. It is a format, the way JSON is a format. There is no magic in it, and once you have seen the raw text, most of the mystery evaporates.

There is one more property to name up front, because it explains an enormous amount of otherwise-baffling behaviour. HTTP is **stateless**: the server keeps no memory of you between requests. When your second request arrives, the server has no idea it just answered your first one. It is not being rude — it genuinely does not remember. Every request has to arrive carrying everything needed to understand it, including who you are.

The mental model to carry: **every request is a letter to a stranger with amnesia.** Nothing carries over. If you want the server to know you have a token, the token goes in *this* letter. If you want it to know you are on page three, page three goes in *this* letter. This is why credentials get attached to every single call rather than logged in once, and it is why "pagination" is a thing you manage rather than a thing that just happens.

---

## 2. The two blocks of text

You have almost certainly never seen a raw HTTP request, so here is one. This is genuinely, byte for byte, roughly what goes down the wire when you fetch a GitHub user:

```
GET /users/torvalds?per_page=10 HTTP/1.1        <- method, path, query
Host: api.github.com                             <- headers
Accept: application/json
User-Agent: my-script/1.0
                                                 <- blank line
<body — usually empty for GET>
```

Read it top to bottom. The first line says three things at once: *what you want done* (`GET`, meaning "read something"), *which thing* (`/users/torvalds`, with `?per_page=10` tacked on as an option), and which version of the protocol you are speaking. Then come several lines of the form `Name: value`. Those are **headers** — extra facts *about* the request rather than the request itself: which server you meant, what format you would like back, what program you are. Then a completely blank line, which is the protocol's way of saying "headers finished." Anything after that blank line is the **body**, the actual payload of data you are sending. A `GET` almost never has one.

The reply has the same shape with a different first line:

```
HTTP/1.1 200 OK                                  <- status line
Content-Type: application/json                   <- headers
X-RateLimit-Remaining: 59

{"login": "torvalds", "id": 1024025}             <- body
```

That first line is the **status line**, and the number in it — `200` — is the **status code**, a three-digit number saying how it went. Then headers again, facts about the response. Then a blank line. Then the body, which here is the JSON you actually wanted, the same kind of JSON you have been picking apart since unit 04.

So when you write `requests.get(url)` in unit 12, what the library does is: build that top block, send it, wait, read the bottom block, and hand you a Python object wrapping it. `r.status_code` is that number off the status line. `r.headers` is that middle section as a dictionary. `r.text` is the body. `r.json()` is the body run through a JSON parser. Nothing more mysterious than that — and when one of those four goes wrong, you now know which part of the text it came from.

The practitioner's detail here: "stateless" describes the *protocol*, not the *connection*. Modern HTTP keeps the TCP connection open and reuses it for several requests in a row, because setting up an encrypted connection is slow and doing it once per request is wasteful. That reuse is exactly what `requests.Session` gives you in unit 15, and on a loop of a hundred calls it is often the single biggest speedup available. The server still remembers nothing; you have just stopped re-dialling the phone.

---

## 3. The anatomy of a URL

A **URL** is the address you are sending that letter to. It looks like one undifferentiated string, but it is made of five named pieces, and the task at the end of this unit is largely about pulling them apart and putting them back together:

```
https://api.github.com/users/torvalds/repos?per_page=100&sort=stars#section
└─┬─┘   └──────┬─────┘└────────┬─────────┘ └───────────┬──────────┘└──┬──┘
scheme       host             path              query string       fragment
```

The mental model: **a URL is a postal address.** The scheme is how it should be delivered, the host is the building, the path is the room inside the building, and the query string is the note attached to the envelope saying what to do once you arrive.

Here is what each piece means:

| Part | Meaning |
|------|---------|
| **scheme** | `https` (encrypted) or `http`. Use https. |
| **host** | which server. DNS resolves it to an IP. |
| **path** | which resource on that server. Hierarchical, `/`-separated. |
| **query string** | after `?`, `key=value` pairs joined by `&`. Filters, paging, options. |
| **fragment** | after `#`. **Never sent to the server** — browser-only. |

Two of those rows deserve more than a table cell. The **scheme** is the first word, before the colon, and it says which protocol to speak. `https` is `http` with the whole conversation encrypted, and there is no reason to use anything else. The **host** is the machine's name; DNS — the internet's phone book — turns that name into a numeric IP address before anything is sent. And the **fragment**, the bit after `#`, is the genuinely surprising one: it is *never transmitted*. Your browser strips it off and uses it locally to scroll to a section of the page. A server has no way of knowing it was there. That is a real interview question and the answer is "nowhere — it doesn't leave the client."

Two optional pieces round it out. A **port** can appear after the host as `:8000`, saying which numbered door on that machine to knock at; it defaults to 443 for https and 80 for http, which is why you normally never see it. And credentials can technically be written as `user:pass@` before the host — an ancient feature you should be aware exists and never, ever use.

One practitioner's wrinkle that will matter in the task: Python's URL parser does not give you a field called `host`. It gives you `netloc`, short for "network location," which is the host *plus* the port *plus* any of that `user:pass@` nonsense, all as one string. For the clean URLs you will meet, `netloc` and host are the same text — but the name is different, and knowing why saves you a confused minute.

---

## 4. Percent-encoding, and why you must never build a query string by hand

This is the most load-bearing paragraph in the lesson, so slow down for it.

A URL is a piece of text where certain characters have *jobs*. `?` means "the query string starts here." `&` means "next parameter." `=` separates a key from its value. `/` separates path segments. `#` starts the fragment. That is fine until the data you want to send *contains one of those characters* — and then there is no way for the server to tell your data apart from the punctuation.

The fix is **percent-encoding**: any character that would be ambiguous gets replaced by a `%` followed by two hexadecimal digits giving its numeric value.

```
space -> %20      &  -> %26      /  -> %2F      é -> %C3%A9
```

The mental model: **percent-encoding is quoting.** It is the same idea as putting quotes around a string in SQL so that a comma inside a value doesn't get read as a column separator. Data goes in quotes; punctuation stays outside.

So a search for `hello world` with an option `a/b` cannot be written as `?q=hello world&x=a/b`. It has to travel as `?q=hello%20world&x=a%2Fb`.

Now the important part. **Do not do this yourself.** Not with an f-string, not with string concatenation, not "just this once because the value is simple." The reason is that the failure mode is silent. Suppose the interviewer's search term is `R&D`. If you paste that into a query string, the `&` reads as a parameter separator, the server sees a parameter `q` with the value `R` and a second, meaningless parameter called `D`, and it returns you a perfectly valid `200 OK` full of results for `R`. Nothing raises. Nothing warns. You get a plausible wrong answer and present it.

This is precisely why `requests` has a `params=` argument that takes a dictionary:

```python
requests.get(url, params={"q": "R&D"})
```

You hand it Python values, it does the encoding, and it is right every time. When you meet that argument in unit 12 it will look like a small convenience. It is not — it is the thing standing between you and quietly wrong results. And in this unit's task you build the same machinery yourself, once, so that you know what it is doing.

One asymmetry worth knowing before it confuses you: inside a query string, a space may legally be encoded either as `%20` *or* as `+`, and Python's `urlencode` chooses `+`. Inside a *path*, only `%20` is valid and `+` means a literal plus sign. Two different rules in two parts of the same URL. The task's third `add_params` example shows exactly this, and the `+` there is correct rather than a bug.

---

## 5. Path parameter versus query parameter

There are two places to put information into a URL and the choice is not arbitrary.

```
/users/torvalds              <- path param: identifies WHICH resource
/users?per_page=10           <- query param: modifies HOW you get it
```

The rough rule is: if removing it makes the URL point at a *different thing*, it belongs in the path. If it filters, sorts, pages, or formats the same thing, it belongs in the query string. `/users/torvalds` and `/users/octocat` are two different resources. `/users?per_page=10` and `/users?per_page=50` are two views of one resource.

You will care about this twice. Now, because it tells you which part of a URL to modify when an interviewer says "now get me page two." And in unit 20, when you build your own API with FastAPI and have to declare both kinds explicitly — at which point this distinction stops being etiquette and becomes syntax.

---

## 6. Methods — the verb at the start of the request

The first word of a request is the **method**, and it says what you want done. There are seven you might meet, and the two columns you should actually read are the last two:

| Method | Meaning | Body? | Safe? | Idempotent? |
|--------|---------|-------|-------|-------------|
| `GET` | read | no | yes | yes |
| `POST` | create / submit / "do something" | yes | no | no |
| `PUT` | replace entirely | yes | no | yes |
| `PATCH` | partial update | yes | no | no |
| `DELETE` | remove | rarely | no | yes |
| `HEAD` | headers only, no body | no | yes | yes |
| `OPTIONS` | what's allowed here | no | yes | yes |

Two words in that table are jargon and both are worth having properly. **Safe** means the request does not change anything on the server — it only reads. **Idempotent** (stress on the *dem*) means doing it five times leaves the server in the same state as doing it once. Deleting a record twice still leaves it deleted, so `DELETE` is idempotent even though it is very much not safe.

Here is why you should care rather than just memorise. **These two properties are what tell you whether it is safe to retry.** Networks time out constantly, and when a request times out you genuinely do not know whether the server received it. If it was a `GET`, shrug and send it again — worst case you read the same data twice. If it was a `POST`, sending it again might create a second record, and now there are two orders where the customer placed one. When you write retry logic in unit 15, this table is the reasoning underneath it, and being able to say *"I'll retry the GETs automatically but not the POSTs, because POST isn't idempotent"* out loud is a genuine signal of experience.

The practitioner's note: `PATCH` is listed as not idempotent and people argue about it, but the reason is real. A patch that says "set status to shipped" is idempotent. A patch that says "add 1 to the view count" is not — run it five times and you have five views. The method's guarantee depends on what the body says, which is exactly why the spec refuses to promise anything.

For the kind of data-extraction task you are preparing for, you will use `GET` for roughly ninety-five percent of everything. Learn the rest so you recognise them; spend your effort on `GET`.

---

## 7. Status codes — the single most useful thing in this unit

Every response starts with a three-digit number. The first digit is the category, and if you learn nothing else from this lesson, learn the categories:

| Range | Meaning |
|-------|---------|
| **1xx** | Informational. You'll never see one. |
| **2xx** | Success. |
| **3xx** | Redirect — the thing is elsewhere. |
| **4xx** | **Your request was wrong.** |
| **5xx** | **The server broke.** |

The mental model: **the first digit tells you whose fault it is.** And the 4xx-versus-5xx split is the one distinction in this entire unit that changes what you actually *do next*. A 4xx means the problem is in the letter you sent — your URL, your parameters, your credentials — and sending the identical request again will fail identically. Stop and fix your code. A 5xx means the letter was fine and something fell over on their end, which is often transient. Wait a moment and send exactly the same thing again.

That is the whole reasoning behind retry logic, and it is why this unit's task asks you to write a function that reports `retryable` and `our_fault` as separate facts.

Now the specific codes. You do not need all of these cold, but the bolded rows are the ones that will actually happen to you:

| Code | Name | What it actually means for you |
|------|------|-------------------------------|
| 200 | OK | Body has your data. |
| 201 | Created | Your POST worked; often a `Location` header points at the new thing. |
| 204 | No Content | Worked, and there's deliberately no body. Calling `.json()` will fail. |
| 301/302 | Moved | `requests` follows these automatically by default. |
| 304 | Not Modified | Your cached copy is still good (see conditional requests below). |
| 400 | Bad Request | Malformed params/body. **Read the response body — it usually says exactly what's wrong.** |
| 401 | Unauthorized | Missing or invalid credentials. Actually means *unauthenticated*. |
| 403 | Forbidden | Authenticated but not allowed — **or rate-limited.** GitHub uses 403 for rate limits, not 429. |
| 404 | Not Found | Wrong path, or that record genuinely doesn't exist. Often normal, not an error. |
| 405 | Method Not Allowed | Right URL, wrong verb. Usually a GET where POST was needed. |
| 422 | Unprocessable | Well-formed but semantically invalid. **FastAPI returns this for validation failures.** |
| 429 | Too Many Requests | Slow down. Look for a `Retry-After` header. |
| 500 | Internal Server Error | Their bug. Retry a couple of times. |
| 502/503/504 | Gateway errors | Infrastructure hiccup. Retry with backoff. |

Four of those rows are worth a sentence each, because each one has caught people out.

**401 versus 403** is a naming disaster baked into the spec since 1997. 401 is *called* "Unauthorized" but actually means "you didn't tell me who you are." 403 means "I know who you are and you still can't have this." If you are getting 401, your token is missing or malformed. If you are getting 403, your token is fine and the permission isn't.

**403 is also GitHub's rate-limit response**, and this is the trap most likely to cost you real minutes in an interview. Almost every API on earth returns 429 when you have made too many requests. GitHub returns 403. So you sit there re-checking your token, convinced you have an authentication problem, when in fact you just need to stop and wait. If you are hitting GitHub and suddenly start getting 403 after a run of successful calls, look at the rate-limit headers before you touch anything else.

**404 is frequently not an error at all.** If you are looking up two hundred usernames and three of them have deleted their accounts, three 404s is the correct and expected outcome. Treating every non-200 as a failure will make you throw away a perfectly good run. Record the misses and carry on — the thread from unit 04 about real data having missing pieces shows up here at the network layer.

**204 will break `.json()`.** It means "that worked and there is deliberately no body." There is nothing to parse, so the JSON parser raises. Check the status before you parse.

---

## 8. Headers — the facts wrapped around the message

A **header** is one line of the form `Name: value`, sitting above the body, carrying information *about* the message rather than being the message. The mental model: **the body is the letter, the headers are what's written on the envelope.** Header names are case-insensitive, which sounds like a footnote and becomes the whole point of the last function in your task.

There are a handful worth sending deliberately:

| Header | Why |
|--------|-----|
| `Accept: application/json` | "Give me JSON." Some APIs return XML otherwise. |
| `User-Agent: my-app/1.0` | Identifies your client. **GitHub rejects requests without one.** |
| `Authorization: Bearer <token>` | Credentials. |
| `Content-Type: application/json` | "My body is JSON." Only relevant when you send a body. |
| `If-None-Match: <etag>` | Conditional request — see below. |

`Accept` is you stating a preference for the format of the reply. `User-Agent` is you naming your program, and GitHub in particular will simply refuse a request that omits it — a genuinely confusing failure the first time it happens, since the URL is perfectly correct. `Authorization` carries your credentials, which we get to in section 10.

And there are a handful worth reading off the response:

| Header | Why |
|--------|-----|
| `Content-Type` | Is it actually JSON? Or an HTML error page? |
| `X-RateLimit-Limit` / `-Remaining` / `-Reset` | Your quota and when it refills. |
| `Retry-After` | Seconds (or a date) to wait before retrying. |
| `Link` | Pagination — GitHub puts `rel="next"` here. |
| `ETag` | Version identifier for conditional requests. |

Two of these matter more than the rest. `Link` is how GitHub tells you there are more pages — it hands you the URL of the next page directly, so you never have to guess at page numbers, and parsing it is one of this unit's task functions. The `X-RateLimit-*` trio tells you how much budget you have left before you get blocked.

**Reading the rate-limit headers proactively rather than waiting to get blocked is a senior-looking move that costs one line.** Print them once at the start of a long pull and you know immediately whether your plan is even feasible, instead of finding out three hundred records in.

The practitioner's detail, and it is the one your task turns into an exercise: because header names are case-insensitive, a server may send you `Retry-After`, `retry-after`, or `RETRY-AFTER` and all three are equally correct. The `requests` library hides this from you completely — its header object is a special case-insensitive dictionary, so `r.headers["retry-after"]` works no matter what came down the wire. A plain Python dictionary is *not* case-insensitive. So the moment you are working with headers from a test fixture, a log file, or anything other than a live `requests` response, you have to normalise the keys yourself. That is exactly the situation `seconds_until_reset` puts you in.

### Conditional requests and ETags

An **ETag** is a short string the server sends alongside a response that acts as a version stamp for that exact content — think of it as a fingerprint of the body. On your next request for the same thing, you send it back as `If-None-Match: <that etag>`, which effectively asks "has this changed since the version I have?" If it hasn't, the server replies **304 Not Modified** with no body at all: a tiny, cheap response instead of a big one. On GitHub, a 304 does not count against your rate limit, which makes this a genuinely useful trick. It is very much an "if I had more time I'd add conditional requests" line rather than something to build first, but knowing it exists is worth the thirty seconds.

---

## 9. Authentication — and the one rule you must not break

Most of the APIs used in this course need no credentials at all, which is deliberate: it keeps you focused on the data. But you will be asked about authentication, so here are the schemes you might be handed:

| Scheme | How | Notes |
|--------|-----|-------|
| None | — | All the APIs in this course. |
| API key in query | `?api_key=abc` | Simplest; leaks into logs and browser history. |
| API key in header | `X-API-Key: abc` | Better. |
| Bearer token | `Authorization: Bearer abc` | The most common. |
| Basic auth | `Authorization: Basic base64(user:pass)` | `requests` does it via `auth=(u, p)`. |
| OAuth2 | Multi-step token exchange | Out of scope; you'd be given a token. |

The one you will almost certainly meet is the **bearer token**. The name is literal: it is a string that grants access to whoever *bears* it, with no further proof of identity required — like a cinema ticket rather than a passport. Anyone holding the string can use it. That is exactly why the next rule exists.

Note also why putting a key in the query string is discouraged: query strings get written into server access logs, proxy logs, and browser history as a matter of routine. A key in a header does not. Same secret, very different blast radius.

**Never hardcode a credential in your source code.** Not in a variable at the top, not in a comment, not "temporarily." Source code gets committed, and a committed secret is a leaked secret even after you delete it, because the history keeps it. Read it from an **environment variable** — a value set in the shell that surrounds your program rather than written inside it:

```python
import os
token = os.environ.get("GITHUB_TOKEN")
```

Note the `.get()`, the same method from unit 04 and for the same reason: if the variable isn't set you want `None` rather than a crash. Saying this out loud when authentication comes up in an interview costs three seconds and is exactly what the interviewer is listening for.

---

## 10. Content types — how to know what you were actually sent

The `Content-Type` header on a response tells you what kind of thing the body is, so you know how to read it. The mental model: **it's the label on the parcel telling you how to open it.**

| Value | Body is |
|-------|---------|
| `application/json` | JSON. `.json()` works. |
| `text/html` | A web page — usually an error page you didn't expect. |
| `text/csv` | CSV text. |
| `application/x-www-form-urlencoded` | Form data (`a=1&b=2`). |
| `multipart/form-data` | File uploads. |

You care about this for one specific moment, which will happen to you: `.json()` raises a `JSONDecodeError` and you have no idea why. The instinct is to assume you have found a bug in the parser. You have not. The body simply isn't JSON. So do two things, in this order — check `Content-Type`, then print `r.text[:300]` to look at the first three hundred characters of what you actually got. Nine times out of ten it is an HTML error page or a login redirect, and it says in plain English what went wrong. Two seconds of looking beats twenty minutes of guessing, which is the same lesson as unit 04's advice to print the type of a nested value when you lose track of it.

The practitioner's detail: the real header value is often `application/json; charset=utf-8`, with a trailing parameter naming the character encoding. So never test it with `==`. Ask whether `"json" in content_type` instead, or the one perfectly good response will look wrong to your code.

---

## 11. Rate limits, and some arithmetic worth doing

A **rate limit** is a cap the server puts on how often you may call it. Exceed it and you get blocked for a while. Two designs are common. A **fixed window** allows some number of requests per period and resets the counter when the period rolls over — sixty per hour, counter cleared on the hour. A **token bucket** refills continuously, so short bursts are fine but sustained hammering gets throttled.

The numbers that matter to you: **GitHub gives an unauthenticated caller 60 requests per hour, per IP address.** With a token, that becomes 5000.

Sit with sixty for a second, because it is smaller than it sounds. A loop over a hundred repositories is not sixty requests, it is a hundred, and it dies two-thirds of the way through. Fetching three pages of results for twenty different users is also a hundred and eighty. You can exhaust an hour's budget in under a minute of ordinary-looking code, and there is no way to un-spend it — you sit and wait. During a timed interview, that is a genuinely bad afternoon.

This is why unit 15 spends its time on caching, and why every loop in this course's later tasks has a hard cap on how many pages it will fetch. It is not tidiness; it is budget management.

When you do get limited, the polite response is: read `Retry-After` if the server sent one and wait exactly that long, and otherwise back off exponentially — wait a second, then two, then four — rather than retrying immediately in a tight loop. Hammering a server that just told you to slow down is how an IP gets blocked outright.

One detail that catches people, and which your task encodes directly: `X-RateLimit-Reset` is not "seconds until reset." It is an absolute Unix timestamp — the number of seconds since 1 January 1970 — naming the moment the window rolls over. To get a duration you subtract the current time from it. Get that backwards and you will sleep for fifty-five years.

---

## 12. Look this up yourself

The task needs a few tools I have deliberately not spelled out, because reading documentation under mild time pressure is the most transferable skill in this course.

- `urllib.parse.urlparse()` and `urlencode()` — you'll need both for the task
- `parse_qs()` vs `parse_qsl()` — and why one returns lists
- What `requests` does with 3xx by default, and `allow_redirects=False`
- HTTP/2 multiplexing (one sentence of awareness is enough)
- CORS — why it exists and why it never affects a Python script (it's a browser rule)
- Idempotency keys for safe POST retries

As always, the fastest route is the interactive prompt. Type `python`, then `from urllib.parse import urlparse`, then `urlparse("https://x.com/a?b=1#c")` and *look at what comes back*. Thirty seconds there tells you more than any paragraph I could write about it.

---

## 13. Check yourself

Answer these before opening the task. If one isn't obvious, reread the section — that's cheaper than getting stuck and not knowing why.

1. What's the practical difference between a 4xx and a 5xx?
2. Which status does GitHub return when you're rate-limited, and why is that surprising?
3. Where does the fragment (`#section`) get sent?
4. Why is retrying a `GET` safer than retrying a `POST`?
5. What header does GitHub require that most APIs don't?
6. `.json()` raised `JSONDecodeError`. What two things do you check first?

*(Answers: 1. 4xx means fix your request; 5xx means wait and retry. 2. 403, where most APIs use 429. 3. nowhere — it never leaves the browser. 4. `GET` is idempotent and safe; a repeated `POST` may create duplicates. 5. `User-Agent`. 6. the `Content-Type` header and `r.text[:300]`.)*

---

*Three things to carry out of this unit. First, a request and a response are just two blocks of text with a status line, some headers and a body, and every attribute `requests` hands you in unit 12 is a slice of one of those blocks — so when something looks wrong, you now know which slice to print. Second, the first digit of the status code tells you whose fault it is, and 4xx-versus-5xx is the difference between fixing your code and simply waiting; the exception that will bite you is GitHub answering rate limits with 403 instead of 429. Third, never assemble a query string by pasting text together, because the failure is silent and produces a confident wrong answer — which is the entire reason `requests` has a `params=` argument, and the reason you are about to build one yourself.*

*The task has no network in it at all. It is pure standard-library URL and header manipulation: pulling a URL apart, adding parameters to it safely, classifying a status code, and reading the two headers that decide whether you may keep going. Every one of those is a thing `requests` will later do for you — you are writing them once so that the library stops being a black box.*

*Now open [`task.py`](task.py).*
