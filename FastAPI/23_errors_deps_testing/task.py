"""Unit 23 task — errors, dependencies, and testing.

You are rebuilding unit 22's GitHub gateway, properly this time. The endpoints
do roughly what they did before; what changes is how the pieces are wired
together, and the wiring is the whole exercise.

Five things are different from unit 22. The HTTP client now arrives through
`Depends`, so the tests can swap it out with `dependency_overrides` instead of
reaching into your module and monkeypatching a function. The paging parameters
live in one reusable dependency rather than being copied into two endpoints.
An optional API key is enforced by a dependency that raises, so no endpoint
needs an `if` at the top. The service layer raises a domain exception that
knows nothing about HTTP, and a single exception handler at the edge decides
what status code that becomes. And a middleware adds a timing header to every
response.

That is the shape you would actually write for a service you had to maintain,
and it is the shape both capstones start from.

Work top to bottom — the file is ordered so that everything you need already
exists by the time you reach it. The docstrings and the comment blocks are the
specification: the tests check exactly what they describe, down to the header
name and the number of decimal places, so read them as a contract rather than
as description. When prose and a stated value disagree, the stated value wins.

Run:  python -m pytest test_task.py -v
      uvicorn task:app --reload
"""

import os
import time

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse

GITHUB = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 10.0
API_KEY_ENV = "GATEWAY_API_KEY"

app = FastAPI(title="GitHub Gateway v2", version="2.0.0")


# --------------------------------------------------------------------------
# Domain exception
# --------------------------------------------------------------------------


class UpstreamError(Exception):
    """Raised by the service layer when the upstream API misbehaves.

    This is your own exception class, describing failures in the vocabulary of
    your problem rather than the vocabulary of HTTP. It records *what went
    wrong* and *while doing what*, and it deliberately says nothing at all
    about status codes — deciding those is the exception handler's job, further
    down the file.

    Write an `__init__(self, kind, context="")` that stores two attributes:

        kind     one of the strings "not_found", "rate_limited", "timeout",
                 "unavailable", "bad_response"
        context  a string naming what was being fetched, for example the
                 username you were looking up

    Both are plain attributes on the instance, and the tests read them
    directly as `exc.kind` and `exc.context`.

    Why bother: in unit 22 the fetching code produced an HTTPException with a
    status code baked in, which meant the code that talks to GitHub had an
    opinion about what your callers should see. Those are two different
    concerns, and separating them is what lets exactly the same service code be
    driven by a command-line script, a background worker, or a test — none of
    which have callers and none of which care what 502 means.
    """

    # TODO


# --------------------------------------------------------------------------
# Dependencies
# --------------------------------------------------------------------------


async def get_client():
    """Hand the endpoints an httpx.AsyncClient, and close it afterwards.

    Build the client with `timeout=TIMEOUT` and `headers=HEADERS`, the two
    module constants defined at the top of the file.

    This must be a GENERATOR dependency, meaning it hands its value over with
    `yield` rather than `return`. Open the client inside an `async with` block
    and `yield` it from inside that block. FastAPI runs everything before the
    `yield` on the way into your endpoint, gives your endpoint the yielded
    client, and comes back to run everything after the `yield` once the
    response has been produced — so the `async with` closes the client for you,
    every time, including when the endpoint raised.

    Write `return httpx.AsyncClient(...)` instead and nothing visible breaks:
    the tests pass, the endpoints work, and you leak one unclosed connection
    pool per request until the process runs out of file descriptors under
    load. That is why the `yield` is not a stylistic preference.

    The second reason this function exists at all is testing. Because the
    endpoints ask for the client through `Depends(get_client)` rather than
    building one themselves, a test can write

        app.dependency_overrides[get_client] = something_fake

    and every endpoint quietly receives the fake instead, with no monkeypatch
    and no change to any line of your code. That is exactly what this unit's
    `test_task.py` does, and it is worth reading its `upstream` fixture before
    you start.
    """
    # TODO
    raise NotImplementedError


def pagination(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """Reusable paging parameters, written once and used by two endpoints.

    The body is one line: return {"limit": limit, "offset": offset}.

    All the interesting work is already done in the signature above. FastAPI
    reads a dependency's parameters exactly the way it reads an endpoint's, so
    those two `Query(...)` declarations become real query parameters on every
    endpoint that depends on this function — documented on the /docs page,
    defaulted to limit 10 and offset 0, and validated before your code runs.
    A request asking for `?limit=0` or `?limit=101` or `?offset=-1` is rejected
    with a 422 that you never wrote a line of. The tests check all three.

    Why bother: two endpoints below need paging. Copying the parameters into
    both means two places to change the maximum, and one day they disagree
    without anyone noticing. Here the rule lives in one function, and the
    endpoints just say they depend on it.
    """
    # TODO
    raise NotImplementedError


def require_api_key(x_api_key: str | None = Header(default=None)):
    """An API-key gate that switches itself off when no key is configured.

    The parameter `x_api_key` reads the request header `X-API-Key` —
    `Header(default=None)` is the header equivalent of `Query`, and FastAPI
    converts the underscores in the parameter name to hyphens for you. When the
    header is absent the parameter is None.

    Three cases, in this order:

      - when the environment variable GATEWAY_API_KEY (the module constant
        API_KEY_ENV holds that name) is unset or empty, authentication is
        DISABLED: return None and let everything through
      - when it is set, the X-API-Key header must match it exactly, otherwise
        raise HTTPException(401, "invalid or missing api key")
      - on success return the key

    Read the expected key from os.environ INSIDE this function rather than at
    import time. This is the non-obvious constraint in the file. If you write
    `EXPECTED = os.environ.get(API_KEY_ENV)` at module level it is evaluated
    once, when Python first imports `task`, and it is frozen from then on. The
    tests set and unset that variable between individual test cases, so a value
    captured at import would be stale for every one of them — and, worse, the
    same thing happens in production the first time someone changes a
    configuration value and restarts nothing.

    On the 401 itself: this is authentication, not authorization. 401 means "I
    do not know who you are." 403 would mean "I know exactly who you are and
    you may not do this." The names in the HTTP specification have those two
    backwards and always will.

    Why bother making this a dependency rather than a check inside each
    endpoint: a dependency that raises stops the request before the endpoint
    function is entered at all, so there is no way to accidentally do the work
    and then reject. And when somebody adds a new endpoint later, forgetting
    the auth means leaving a parameter out of the signature, which is visible,
    rather than forgetting an `if`, which is not.
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------
# Exception handler and middleware
# --------------------------------------------------------------------------


# TODO: register the one function in this program that is allowed to know both
# vocabularies — your domain's and HTTP's.
#
# Whenever an UpstreamError escapes any endpoint, FastAPI should catch it and
# send this response instead. Write an async function taking (request, exc) and
# put the decorator @app.exception_handler(UpstreamError) on it. Return a
# JSONResponse, which is the object you build when you want to set the status
# code and the body yourself rather than letting FastAPI infer them from a
# return value.
#
# The mapping from kind to status and detail, in full:
#
#   kind            status   detail
#   not_found       404      f"not found: {context}"
#   rate_limited    429      "upstream rate limited"
#   timeout         504      "upstream timeout"
#   unavailable     503      "upstream unavailable"
#   bad_response    502      "upstream returned an unusable response"
#   anything else   502      "upstream error"
#
# The response body is exactly {"detail": <detail>, "kind": <kind>}. Sending
# the kind back as well as the sentence means a client can branch on a stable
# short string instead of pattern-matching English prose.
#
# The last row matters more than it looks. A kind you never anticipated still
# has to produce a valid response rather than crashing inside the handler that
# exists to stop crashes, so the lookup needs a fallback rather than assuming
# the key is present.
#
# Note which failures become which status. GitHub returning a 500 to you is a
# 502 going out, because it is their bug and not yours; conflating the two
# makes your own error rate unreadable and gets you paged for someone else's
# outage. A timeout is 504 and an unreachable host is 503, and both of those
# tell the caller that retrying is reasonable.


# TODO: register an http middleware — code that wraps every request on its way
# in and every response on its way out, outside your endpoints and outside your
# dependencies.
#
# Write an async function taking (request, call_next) and decorate it with
# @app.middleware("http"). Anything before `response = await call_next(request)`
# runs on the way in; call_next runs the rest of the application; anything
# after runs on the way out. You must return the response, or nothing reaches
# the caller.
#
# Measure how long the request took and set the response header
# "X-Process-Time" to the elapsed seconds formatted to 4 decimal places — an
# f-string with :.4f does that. Use time.perf_counter() rather than time.time()
# to take the readings, because perf_counter is a monotonic clock intended for
# measuring intervals and cannot jump backwards if the system clock is
# adjusted mid-request.
#
# Because middleware sits outside everything, this header appears on responses
# your endpoints never produced — including the error responses from the
# handler above. That is exactly what you want when you need to know whether a
# 504 took ten seconds or ten milliseconds. The test asserts the header is
# present on /health.


# --------------------------------------------------------------------------
# Service layer -- no HTTP concepts, raises UpstreamError
# --------------------------------------------------------------------------


async def fetch(client, path, params=None, context=""):
    """GET {GITHUB}{path} with the given client and return the parsed JSON.

    The happy path is three lines: build the URL by joining the GITHUB
    constant to `path`, `await client.get(url, params=params)`, call
    `response.raise_for_status()` so a bad status becomes an exception, and
    return `response.json()`.

    Everything else is translation. Wrap the call in a try and turn each kind
    of httpx failure into an UpstreamError:

      404                       -> kind "not_found"
      429                       -> kind "rate_limited"
      any other bad status      -> kind "bad_response"
      httpx.TimeoutException    -> kind "timeout"
      other httpx.RequestError  -> kind "unavailable"

    Every UpstreamError you raise carries the `context` you were given, so the
    handler further up can say *what* was not found rather than just that
    something wasn't.

    The order of the except clauses is load-bearing, and this is the detail
    worth slowing down for. `httpx.HTTPStatusError` — what raise_for_status
    produces — is not a `RequestError` at all; they are separate branches of
    the exception tree, because one means "they answered, badly" and the other
    means "they did not answer." But `httpx.TimeoutException` IS a subclass of
    `RequestError`. Python tries except clauses top to bottom and takes the
    first one that matches, so if you catch `RequestError` before
    `TimeoutException`, every timeout is swallowed by the broader clause and
    reported as "unavailable". Nothing errors; you just silently get the wrong
    kind, and therefore the wrong status code. Catch the specific one first.

    Use `raise UpstreamError(...) from exc` so the original exception is
    recorded as the cause. Your logs then show both your exception and the
    httpx one underneath it with the real line number, which is the difference
    between a two-minute diagnosis and an hour of guessing.

    Notice what this function does not contain: any status code going OUT. It
    knows GitHub sent a 404; it has no opinion about what your caller should
    receive. That separation is what this entire unit is about. In unit 22 the
    equivalent function produced an HTTPException, and moving that decision to
    the edge is the upgrade.
    """
    # TODO
    raise NotImplementedError


def slim_repo(repo):
    """Reduce a raw GitHub repo dict to just {name, stars, language, archived}.

    Take the four fields you care about out of the large record GitHub sends
    and return a small flat dictionary with exactly those four keys. The star
    count lives under GitHub's own name, "stargazers_count", and comes out
    under yours, "stars".

    Missing fields must not crash it. A repo with no stars field counts as 0,
    a missing language is None, and `archived` is coerced to a real bool so a
    missing value becomes False rather than None. Unit 04's .get() with a
    default is the whole technique.

        slim_repo({"name": "b", "stargazers_count": 5,
                   "language": "Python", "archived": False})
            -> {"name": "b", "stars": 5, "language": "Python",
                "archived": False}

        slim_repo({"name": "x"})
            -> {"name": "x", "stars": 0, "language": None, "archived": False}

    Why bother: this function is pure — a dict goes in, a dict comes out, and
    it touches no client, no request, and no app. That means its tests are two
    lines each and need no HTTP at all, which is unit 06's fetch-and-transform
    split paying off one last time. Every piece of logic you can move to this
    side of the line is a piece you can verify for free.
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------


# Four routes. Write them with @app.get(...) exactly as in units 20 to 22; the
# only new thing is that the pieces they need arrive as Depends(...) parameters
# rather than being built inside the function.
#
# Three of the four sort their results the same way, so you may want one small
# private helper that ranks a list of slimmed repos: stars descending, then
# name ascending as the tiebreaker. Sorting by a tuple key with the number
# negated is unit 07's technique, and having a deliberate tiebreaker is what
# stops the same data coming back in a different order between runs.


# GET /health
#   Takes NO dependencies at all.
#   -> {"status": "ok", "auth_required": <bool>}
#   auth_required reflects whether GATEWAY_API_KEY is currently set, read
#   fresh from os.environ, so the answer is honest at the moment of asking.
#
#   The absence of dependencies here is a deliberate design decision rather
#   than an oversight, and it is worth being able to defend out loud. A health
#   check that requires credentials is useless to a load balancer, which has
#   none and will simply mark you dead. And a health check that calls upstream
#   makes your own liveness signal depend on somebody else's uptime — GitHub
#   has a bad hour, your monitor concludes your service is down, and something
#   restarts a process that was working perfectly. This route answers one
#   question: is this process alive and able to respond? Nothing else.


# GET /users/{username}
#   Dependencies: get_client, require_api_key
#   Fetches /users/{username} through your fetch() and returns
#   {"login":..., "name":..., "followers":..., "public_repos":...}
#   with missing numbers defaulting to 0.
#
#   Pass the username through as fetch's `context`, so a 404 from GitHub comes
#   back to the caller saying which user was not found.
#
#   Note there is no try/except anywhere in this endpoint. An UpstreamError
#   raised down in fetch travels straight up through here and out to the
#   exception handler you registered above. The endpoint stays about the happy
#   path, which is most of what makes this arrangement pleasant to read.


# GET /users/{username}/repos
#   Dependencies: get_client, pagination, require_api_key
#   Fetches /users/{username}/repos with params {"per_page": 100}, slims each
#   repo, ranks them (stars descending, then name ascending), and then applies
#   the pagination window -- offset items in, limit items long.
#   -> {"username":..., "total": <before paging>, "count": <returned>,
#       "limit":..., "offset":..., "items":[...]}
#
#   "total" is how many you had before paging; "count" is how many you are
#   actually returning. Sending both means the caller can work out whether
#   there is another page without asking for one.
#
#   The dependency you never use gets an underscore name -- _key: str | None =
#   Depends(require_api_key) -- because you want the check to run, not the
#   value it returns.


# GET /search/repos
#   Dependencies: get_client, pagination, require_api_key
#   Query parameter: q -- required, 2..100 characters. Declare it with
#   Query(min_length=2, max_length=100); a missing or out-of-range q must be
#   rejected with a 422 you do not write.
#   Calls /search/repositories with params {"q": q, "per_page": 100}.
#
#   The response here is an ENVELOPE rather than a bare list:
#   {"total_count": n, "items": [...]}. So reach into it for the items, slim
#   and rank them the same way, then page them.
#
#   -> {"q":..., "total": <total_count from the API>, "count": <returned>,
#       "limit":..., "offset":..., "items":[...]}
#
#   The one thing to get right here: "total" comes from the upstream's own
#   total_count, NOT from len(items). GitHub returns at most 100 repositories
#   per page but tells you in total_count how many actually matched, which may
#   be tens of thousands. Reporting len(items) would tell your caller that a
#   search matching 4321 repositories matched 3, which is not a rounding error
#   but a wrong answer. Passing on the honest number is the whole point of the
#   endpoint, and the test says so in its assertion message.
