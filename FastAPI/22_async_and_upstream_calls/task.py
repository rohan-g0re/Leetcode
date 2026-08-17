"""Unit 22 task — async upstream calls with httpx.

You are building a small service that sits IN FRONT of the GitHub API. Somebody
calls your endpoint, you call GitHub, and on the way back you reshape the data,
cache it, fan out to several users at once, and turn GitHub's failures into
honest statuses of your own. A service in that position is called a gateway,
and building one is exactly the "wrap this endpoint and add something useful"
task that interviewers reach for.

Work top to bottom. The four helper functions come first because the five
endpoints at the bottom are built out of them, so a helper you got right is a
helper you never have to think about again.

About the tests. They replace `get_client` with a fake client that returns
canned responses, which means every piece of logic here — the cache, the
fan-out, the error translation, all five routes — is checked with no network at
all, in milliseconds. That is only possible because there is exactly one place
in this module where a client comes from. Do not construct your own client
anywhere else; call `get_client()`.

    python -m pytest test_task.py -v -m "not live"    # offline, the ones that matter
    python -m pytest test_task.py -v                  # also hits GitHub for real

    uvicorn task:app --reload      then open /docs
"""

import asyncio
import time

import httpx
from fastapi import FastAPI, HTTPException, Query

GITHUB = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 10.0
CACHE_TTL_SECONDS = 60

app = FastAPI(title="GitHub Gateway", version="1.0.0")

# username -> (fetched_at_epoch, payload). Provided for you.
_CACHE: dict[str, tuple[float, dict]] = {}


def reset_cache():
    """Clear the cache. Used by the tests; provided for you."""
    _CACHE.clear()


def get_client():
    """Return the httpx.AsyncClient to use for upstream calls.

    Provided for you. The tests monkeypatch THIS function to hand back a fake
    client, which is why every other function must call it rather than
    constructing a client of its own.
    """
    return httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS)


# --------------------------------------------------------------------------
# Upstream helpers
# --------------------------------------------------------------------------


async def fetch_json(client, url, params=None):
    """GET `url` with the given client and return the parsed JSON.

    Three lines, and they are the three lines from the lesson: await the GET,
    call raise_for_status() so that a 4xx or 5xx becomes an
    httpx.HTTPStatusError rather than being silently treated as data, and
    return response.json().

    Pass `params` straight through to the client. One of the tests checks that
    it arrives, because the repos endpoint later depends on it to send
    per_page=100.

    This function deliberately does no error handling of its own. Its job is to
    turn a URL into data or into an exception; deciding what an exception means
    for the caller is `upstream_error`'s job, one function down. Keeping those
    two concerns apart is why both stay small.
    """
    # TODO
    raise NotImplementedError


def upstream_error(exc, context=""):
    """Translate an httpx exception into the HTTPException you should send back.

    Your caller did not call GitHub — they called you. So when GitHub fails,
    you owe them a status code that describes their situation rather than a
    raw upstream error. This is the mapping, and it is the whole function:

      HTTPStatusError with status 404  -> 404, detail f"not found: {context}"
      HTTPStatusError with status 429  -> 429, detail "upstream rate limited"
      HTTPStatusError with any 4xx     -> 502, detail "upstream error: <status>"
      HTTPStatusError with any 5xx     -> 502, detail "upstream error: <status>"
      httpx.TimeoutException           -> 504, detail "upstream timeout"
      any other httpx.RequestError     -> 502, detail "upstream unreachable"

    `context` is whatever the caller was asking about — a username, usually —
    so the 404 detail can name it. It defaults to an empty string because some
    of the branches do not need it.

    RETURN the HTTPException; do not raise it. That sounds fussy and is not:
    a function that returns an exception object can be called directly in a
    test and its result inspected, which is exactly what the tests do. The
    endpoints then write `raise upstream_error(exc, context=username)`.

    One ordering trap. httpx.TimeoutException is a SUBCLASS of
    httpx.RequestError, which means an `except httpx.RequestError` branch will
    happily catch timeouts too and you will never reach the 504. Check the
    specific one first. The same applies if you write this with isinstance
    checks rather than except clauses — most specific first, always.
    """
    # TODO
    raise NotImplementedError


async def get_user(client, username):
    """Fetch one GitHub user, going through the module cache.

    The cache is `_CACHE`, and it maps a username to a two-item tuple of
    (the time we fetched it, the payload we got). Storing the time is what lets
    you implement a TTL — a maximum age past which an entry is considered
    stale.

    So:

    - look the username up in _CACHE. If there is an entry and it is less than
      CACHE_TTL_SECONDS old, return the stored payload and make NO request at
      all. `time.time()` gives you the current time in seconds, so the age of
      an entry is one subtraction.
    - otherwise fetch {GITHUB}/users/{username}, store (time.time(), payload)
      in _CACHE under that username, and return the payload.

    Let httpx exceptions propagate out of here untouched. Translating them is
    the endpoint layer's job, and it needs the original exception to do it.

    Two things the tests check specifically. The second call for the same
    username must not reach the client at all — that is the entire point of a
    cache. And **a failed fetch must never be cached**: if you record an error,
    every caller for the next minute gets that error without you even retrying.
    You get this right for free by putting the cache write on the line AFTER
    the await, since an exception never reaches the next line.
    """
    # TODO
    raise NotImplementedError


def summarize_user(user):
    """Reduce a raw GitHub user payload to the handful of fields you expose.

    GitHub's user response has around thirty fields and your callers want five
    of them. Choosing a small, stable response shape rather than forwarding
    whatever the upstream happens to send is one of the main reasons to build a
    gateway at all — it means an upstream change does not automatically become
    your callers' problem. Return exactly this dictionary:

    {
      "login": ..., "name": <or None>, "followers": <int, 0 if missing>,
      "public_repos": <int, 0 if missing>, "created_year": <int or None>,
    }

    A pure function — no network, no cache, nothing awaited. Given the same
    payload it always returns the same dictionary, which is what makes it
    trivially testable.

    Real payloads are missing fields, so unit 04's `.get()` with a default is
    the tool here rather than square brackets. Note that the defaults differ on
    purpose: a missing follower count reads better as 0 than as null, but a
    missing name is genuinely unknown and should stay None rather than becoming
    an empty string.

    `created_at` arrives as a string like "2011-01-25T18:44:36Z" and you want
    the year out of it as an integer. The first four characters are the year;
    unit 02's slicing is enough, no date library required. Guard the case where
    the field is absent altogether — created_year is then None.
    """
    # TODO
    raise NotImplementedError


async def get_many_users(client, usernames, concurrency=5):
    """Fetch several users CONCURRENTLY and report both successes and failures.

    This is the fan-out — one request in, many requests out — and it is the
    thing that makes an async gateway worth building. Done sequentially, ten
    users at 200ms each is two seconds. Done concurrently it is about 200ms.

    Return a two-item tuple, (results, errors), where:

      results = [summarize_user(payload), ...] for the usernames that worked,
                in the SAME ORDER as `usernames`
      errors  = [{"username": ..., "error": "<ExceptionClassName>"}, ...]
                for the ones that failed, in the same relative order

    The error entry records the exception's class name as a string — the name
    of the type, not the message. `type(exc).__name__` is how you get it.

    There are three separate requirements here and the tests measure each one
    on its own, so satisfying two of them is not enough:

      1. The requests must overlap. Use asyncio.gather; a loop that awaits one
         request at a time is correct but slow, and there is a timing test that
         fails it.
      2. One failure must not lose the other results. By default a single
         exception inside gather discards every successful result too, so pass
         asyncio.gather(..., return_exceptions=True) and sort the outcomes
         apart yourself with isinstance(outcome, Exception).
      3. At most `concurrency` requests may be in flight at any moment. Use an
         asyncio.Semaphore — the fake client counts its own peak concurrency
         and a test asserts you never exceeded the cap.

    The ordering guarantee is not decoration either: gather returns results in
    the order you passed the coroutines in, regardless of which finished first,
    which is precisely what lets you zip the outcomes back against `usernames`
    and know which failure belongs to which name.

    Duplicate usernames in the input are fine and need no special handling —
    the cache in get_user absorbs them.
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------
#
# Five routes, specified below. Each one is a short function; the work is
# already done in the helpers above. The recurring shape for the async ones is
# to get a client from get_client(), do the work inside a try, translate any
# httpx.HTTPError with upstream_error and raise what it hands back, and close
# the client in a finally so it is closed whether or not things went well.
# httpx.HTTPError is the common ancestor of HTTPStatusError and RequestError,
# so a single except clause covers everything upstream_error knows about.


# GET /health
#   -> {"status": "ok", "cached_users": <len(_CACHE)>}
#
#   A plain `def` is right here, not `async def`: this handler does no I/O at
#   all, so there is nothing to await and nothing to gain. Reporting how many
#   entries are in the cache turns a box-ticking health check into something
#   you can actually watch.


# GET /users/{username}
#   async. Fetch the user through get_user, so that the cache applies, and
#   return summarize_user's output — the trimmed five-field shape, not the raw
#   GitHub payload. A test checks that "avatar_url" is absent from your
#   response, which is its way of checking you really did reshape it.
#
#   Catch any httpx error and raise what upstream_error gives you, passing the
#   username as `context` so a 404 detail names the user who was not found.
#   That single line is what turns GitHub's 404 into your 404, GitHub's 500
#   into your 502, and a timeout into your 504 — all three are tested.


# GET /users/{username}/repos
#   async. Two query parameters:
#       limit int = 5, at least 1 and at most 100
#       sort  str = "stars", and the only permitted values are "stars" or "name"
#
#   Fetch {GITHUB}/users/{username}/repos with per_page=100 as a query
#   parameter, then reshape each repository into
#   {"name":..., "stars":..., "language":..., "archived":...}.
#   GitHub calls the star count "stargazers_count"; you are renaming it, which
#   is the same reshaping-for-your-callers idea as summarize_user.
#
#   Order them by stars descending, with ties broken by name ascending, when
#   sort is "stars"; by name ascending when sort is "name". Then cut the list
#   down to `limit` items.
#
#   -> {"username": ..., "count": n, "items": [...]}
#      where count is how many items you are actually returning.
#
#   Both parameter constraints must produce a 422 when violated, and you should
#   get that from Query rather than by writing an if statement — declaring the
#   rule where the parameter is declared means FastAPI enforces it before your
#   function runs AND documents it in /docs. limit takes ge and le; sort takes
#   a pattern.


# GET /compare
#   async. One required query parameter, `users`: a comma-separated list of
#   between 1 and 10 usernames.
#
#   Split it on commas, strip the whitespace off each name, and drop any empties
#   ("a,, ,b" is two names, not four). Then fetch them all concurrently via
#   get_many_users and assemble:
#
#   -> {
#        "requested": <how many names were asked for, after cleaning>,
#        "found": <how many came back successfully>,
#        "failed": [ {"username":..., "error":...}, ... ],
#        "users": [ <summaries, sorted by followers descending> ],
#        "total_followers": <sum of followers over the successful ones>,
#      }
#
#   Reporting the successes and the failures side by side is the honest answer
#   for a fan-out — nine users plus a note about the tenth beats a blanket
#   error.
#
#   Asking for zero names, or for more than 10, is a 400 whose detail mentions
#   the limit of 10. This is the one validation you DO write by hand, and the
#   reason is worth naming: Query validates the raw string that arrived, but
#   the constraint here is on the LIST you get after splitting and cleaning it,
#   which does not exist until your function runs. When a rule depends on
#   something you computed, it cannot live in the signature.


# DELETE /cache
#   -> {"cleared": <how many entries were removed>}
#
#   Plain def — no I/O. Count the entries before you clear them, since after
#   clearing there is nothing left to count.
#
#   Operational endpoints like this cost two lines and make a caching service
#   demonstrable rather than merely claimed, which is worth doing the moment
#   you have said the word "cache" out loud in an interview.
