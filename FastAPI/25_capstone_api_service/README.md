# 25 — Capstone B: Build an API on Top of an API

*This is the last thing you build in the course, and like unit 24 it is a brief rather than a lesson. There is nothing new in it. Every piece you are about to write is something you already wrote in units 21, 22 or 23 — the models, the async fan-out, the TTL cache, the dependency injection, the central error handler — and the work of this capstone is deciding which of them goes where. Budget about two hours. If the first capstone was the interview question "here is a URL, tell me something useful," this one is the other question they ask, which is "wrap this endpoint in a service of your own."*

---

## The brief

Imagine the interviewer says this, and then stops talking:

> *"We use the GitHub API but it's noisy and rate-limited. Build us a small internal service that exposes just what we need, with sane defaults and some analysis on top. Make it documented and testable."*

That is four sentences and it contains at least six decisions they have not made for you. "Just what we need" means you choose the fields. "Sane defaults" means you choose the page size and the cache lifetime. "Some analysis on top" means you decide what is worth computing about a GitHub user, which is a product question wearing an engineering costume. And "documented and testable" is the part most candidates skip and the part that is easiest to score on, because FastAPI gives you the documentation for free and unit 23 gave you the three tests that matter.

The service you are building sits between your callers and GitHub. Unit 22 gave that position a name: it is a **gateway**, a service whose whole job is to stand in front of another service and add something on the way through — caching, a friendlier response shape, honest error translation. You are not replacing GitHub. You are being a better front door to it.

---

## What you are building

`service.py`, a FastAPI app over `https://api.github.com`, with six endpoints.

| Endpoint | Does |
|----------|------|
| `GET /health` | liveness + cache size. Never requires auth. |
| `GET /users/{username}` | one user, slimmed |
| `GET /users/{username}/repos` | their repos, paged, sorted, filterable |
| `GET /users/{username}/report` | **the interesting one** — fetches the user *and* their repos, computes language breakdown, star distribution, and activity, and returns one report |
| `GET /compare` | several users concurrently, ranked |
| `DELETE /cache` | clear the cache |

Five of those six are a single upstream call with some reshaping around it, and you could write any of them from unit 22 alone. `/users/{username}/report` is the one worth building carefully, because it is the only endpoint where your service does something a caller could not trivially do for themselves: it makes two upstream calls at once with `asyncio.gather`, waits roughly as long as the slower of the two rather than the sum of both, and then combines the two payloads into a single answer that GitHub never offers. That combination — **fan-out**, unit 22's word for one request in and several requests out — is the entire argument for a gateway existing. It is also the endpoint you will demo, so it is where the effort belongs.

---

## The five decisions you will be asked to defend

Everything above describes what the service does. What follows is the part an interviewer asks about *after* the demo, once the `/docs` page is on screen and working, when the questions stop being "does it run" and start being "why is it like that." There are five of them and they are predictable enough that you can rehearse. Writing your answers down before you start coding is that rehearsal — the point is not the document, it is having already said the sentence once so it arrives smoothly the second time.

**The cache TTL.** A **TTL** is a time to live: the age past which a cached entry stops counting as good and you go and fetch again. Yours is set to sixty seconds, and both directions of that dial cost you something real. Make it longer and you are serving follower counts from an hour ago as though they were current, which is fine for a dashboard and wrong for anything someone is about to act on. Make it shorter and you spend your rate limit — unauthenticated GitHub gives you sixty requests an hour, which a single enthusiastic caller can exhaust before lunch. Sixty seconds is a defensible middle: long enough that a burst of traffic about one popular user collapses into one upstream call, short enough that nobody is looking at genuinely stale data. The answer an interviewer wants is not the number, it is that you know what sits on each side of it.

**The status mapping.** An upstream 404 becomes your 404, because the thing your caller asked for genuinely does not exist and that meaning survives the translation intact. But an upstream 500 becomes your **502**, not your 500, and the distinction is worth being sharp about. A 500 from you means *you* are broken. If you emit one when GitHub is down, you have filed a bug against yourself: your caller retries against a thing that was never wrong, your monitoring pages your on-call engineer, and an hour later somebody discovers your code was fine all along. 502 says "my dependency gave me garbage," 504 says "my dependency was too slow," 503 says "I could not reach my dependency at all," and 429 passes straight through because when GitHub throttles you the honest move is to propagate that pressure rather than absorb it and keep hammering. Unit 23's table has all of this; what you are being asked for here is the sentence underneath it, which is that a status code exists to tell a machine whose fault this is and whether retrying is worth it.

**Partial failure in `/compare`.** Somebody asks you about five users and the third one does not exist. You can fail the whole request, or you can return four users and a `failed` list naming the fifth. Return the four. The reasoning is the one unit 22 made about `return_exceptions=True`: throwing away four good answers because of one bad name is a worse service than reporting both, and the caller can do nothing useful with a blanket failure except guess which name was wrong. Reporting "requested 5, found 4, here is the one that failed and why" is more work by about six lines and reads as considerably more mature, because it is what a service that has been used in anger ends up doing.

**The concurrency cap.** `asyncio.gather` is enthusiastic — hand it three hundred coroutines and it will genuinely try to open three hundred connections. A **semaphore**, unit 22's counter-with-a-cap, holds a fixed number of tickets so that only `MAX_CONCURRENCY` requests are ever in flight at once and the rest wait their turn. It is worth being clear that the cap is not there to protect *you*; your event loop would cope. It is there to stop you being rude to GitHub, who will rate-limit or block you if you are, and to stop your process running out of sockets. Mentioning a concurrency cap before anyone asks is one of the strongest "I have actually run this against a real API" signals available to you, because everybody who has read a tutorial knows `gather` and only the people who have been throttled reach for the semaphore in the same breath.

**Response filtering.** Every endpoint declares a `response_model` — a Pydantic model, from unit 21, that FastAPI uses both to document the response on `/docs` and to filter what actually goes out. Filtering is the word to stress. If GitHub adds a field tomorrow, or returns an email address on a user, your response does not change, because anything you did not declare is dropped on the way out. That makes `response_model` a **safety property** rather than a tidiness one: it means your response shape is something you decided rather than something GitHub decides on your behalf, and the day an upstream starts including something sensitive you are already not forwarding it. There is a test in `test_service.py` that asserts exactly this, and its failure message says so out loud.

Write your answers as comments at the top of `service.py`, in the `DESIGN DECISIONS` block that is already there waiting for them. Three sentences each is plenty.

---

## The rules

**The upstream client arrives via `Depends`, never as a module global.** Unit 23 called a dependency a *seam* — a declared place in your app where something can be swapped — and this is the seam the entire test suite stands on. Because `get_client` is a dependency, `test_service.py` can write `app.dependency_overrides[service.get_client] = ...` and hand your app a fake client that returns canned responses, and your code neither knows nor cares. That is **dependency injection**: the thing you need is handed *to* you rather than fetched *by* you. Build the client inside your handler instead and the tests cannot reach it, which means every one of them needs a live network and a GitHub account that is not rate-limited.

**The service layer knows nothing about HTTP status codes.** Your **service layer** is everything that does real work — `fetch`, `cached_fetch`, `get_user`, `get_repos` — as opposed to the endpoints, which deal with the web. When something goes wrong upstream, those functions raise `UpstreamError` carrying a `kind` like `"timeout"` or `"not_found"`, and that is all. One registered exception handler at the edge of the app turns a kind into a status code, and it is the only function in the whole file that speaks both languages. Unit 23's image for this is a border post, and it is worth keeping: inside, everyone talks about what actually went wrong; outside, everyone talks HTTP. The practical payoff is that the same fetching code could be driven by a cron job or a script tomorrow, and a 502 means nothing to a cron job.

**All analysis lives in pure functions.** `build_report(user_payload, repo_payloads)` takes two raw dictionaries and returns a dictionary. No client, no request, no `app`. That is unit 06's fetch-and-transform split, which you first met on a single function, now applied at the scale of a whole service — and the reason to insist on it is that the transform half is always the cheapest thing in a codebase to test. The tests for your report logic hand it two hardcoded dicts and check the numbers, in milliseconds, with the wifi off. Every line of logic you can move to that side of the line is a line you get to check for free.

**Cap the fan-out.** A semaphore, as above. This is a rule rather than a suggestion because the failure mode is not slowness; it is your IP being throttled halfway through a demo.

**Never leak an upstream field you did not declare.** `response_model` does the work, but only if you actually declare the models properly rather than returning raw dicts and hoping. The test that checks GitHub's `email` field never reaches your caller exists precisely because "just pass it through" is the tempting shortcut.

---

## The deliverable

`service.py` in this folder, with every stub filled in and the tests passing.

```powershell
python -m pytest test_service.py -v -m "not live"   # the logic, no network
python -m pytest test_service.py -v                 # the same plus real GitHub
uvicorn service:app --reload                        # the actual service
```

Run the first command constantly and the second one occasionally — `-m "not live"` deselects the three tests that need real GitHub, so the first command works on a train and does not spend your rate limit.

Then open `http://127.0.0.1:8000/docs` and try `/users/pallets/report`. That page is your demo, and it is worth understanding why it is a good one. You did not write a line of it: FastAPI generated an interactive documentation page from your type hints and your response models, so every field of every response is described, every query parameter shows its allowed range, and the interviewer can click a button and see real data come back. Showing that beats talking about your code, and it takes ten seconds.

There is deliberately no `hints.md` for the capstones. Everything here is a recombination of units 21, 22 and 23, and going back to find your own earlier answer is the exercise rather than a detour from it. The worked solution, including written answers to the five design questions, is at [`solutions/25_capstone_api_service.py`](../solutions/25_capstone_api_service.py) — but sit stuck for twenty minutes first, because that is where the learning happens.

---

## Self-assessment

When the tests pass, go back through and score yourself honestly. This one stays a checklist because it is genuinely a list of separate things to check.

| | |
|---|---|
| ☐ | Can you swap the entire upstream for a fake without touching `service.py`? |
| ☐ | Does a dead upstream give 502/504, never 500? |
| ☐ | Is the analysis testable with a hardcoded dict? |
| ☐ | Does `/docs` describe every response shape? |
| ☐ | Can you explain your cache TTL choice? |
| ☐ | Would 20 concurrent `/compare` calls get you rate-limited? |

The last two are the ones no test can check for you, and they are the two an interview actually turns on.

---

## If you have extra time

Only once the base version passes, because finished-and-plain beats ambitious-and-broken every time. Add the `X-Process-Time` middleware from unit 23, which is five lines and visible in the browser's network tab, so it makes the service look finished for almost no cost. Add a `GET /rate-limit` that proxies GitHub's own `/rate_limit`, which is the endpoint you will want the first time you wonder why everything started returning 429. Read a `GITHUB_TOKEN` from the environment and send it upstream — sixty requests an hour becomes five thousand, and it is two lines in your headers dictionary. Add ETag-based conditional requests so a cache refresh that finds nothing changed costs you nothing against your limit. Or persist the cache to disk so a restart does not throw it away, which is the toy version of the sentence "in production this would be Redis."

---

*What makes this a capstone is the same thing that made unit 24 one: nothing in it is new and everything in it is yours to place. Unit 21 gave you the models that now double as your response filter, unit 22 gave you the async fan-out, the TTL cache and the honest translation of somebody else's failures, and unit 23 gave you the dependency that is also a test seam and the one handler that keeps HTTP at the edge. The course has been building toward a service you could hand to another person and let them maintain, and this is it. Now open [`service.py`](service.py), write your five answers at the top, and work down the file — the docstrings are the specification.*
