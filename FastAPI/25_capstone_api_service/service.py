"""Capstone B — a GitHub gateway service.

    uvicorn service:app --reload      then open /docs
    python -m pytest test_service.py -v -m "not live"

This is the last file you write in the course. It is a gateway, in unit 22's
sense: a service that stands in front of somebody else's service and adds
something on the way through. Your callers ask you; you ask GitHub; you cache
the answer, reshape it, analyse it, and hand back something better than what
you received.

Nothing here is new. The models are unit 21, the async fan-out and the TTL
cache are unit 22, and the dependency injection and the single central error
handler are unit 23. What is new is that nobody is telling you which piece
goes where — that decision is the exercise.

Work top to bottom. The file is already laid out in the order the pieces
depend on each other: the exception and its handler, then the models, then the
dependencies, then the service layer that talks to GitHub, then the pure
analysis functions, then the endpoints that tie them together. Each docstring
is the specification for the thing beneath it; where a docstring and your
intuition disagree, the docstring wins, because the tests were written from it.

Read README.md first, and write your five design-decision answers below before
you start coding. These are not busywork and they are not marking. They are
the five questions an interviewer asks out loud once the demo is working and
the conversation turns from "does it run" to "why is it like that." Writing
three sentences on each now means you have already said the sentence once, so
it comes out smoothly the second time.

DESIGN DECISIONS
----------------
1. cache TTL:
   (Why CACHE_TTL_SECONDS is what it is. What goes wrong if it is much longer
   — and what goes wrong if it is much shorter, given sixty unauthenticated
   requests an hour.)

2. status mapping:
   (Why an upstream 404 becomes your 404, but an upstream 500 becomes your 502
   rather than your 500. Who gets paged in each case.)

3. partial failure:
   (In /compare, one name out of five does not exist. Do you fail the whole
   request or return four users and a `failed` list? Say why.)

4. concurrency cap:
   (Why bound the fan-out at all, when your event loop would happily run
   three hundred requests at once. Who the cap actually protects.)

5. response filtering:
   (Which upstream fields you deliberately do not expose, and why declaring a
   response_model is better than passing the upstream payload through.)
"""

import asyncio
import os
import time

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

GITHUB = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 10.0
CACHE_TTL_SECONDS = 60
MAX_CONCURRENCY = 5

app = FastAPI(
    title="GitHub Insights",
    description="A slimmed, cached, analysed view of the GitHub API.",
    version="1.0.0",
)

# key -> (fetched_at, payload). Provided for you.
_CACHE: dict[str, tuple[float, object]] = {}


def reset_cache():
    """Empty the cache.

    Provided for you, and used by the tests rather than by your code. Every
    test runs with a clean cache so that one test's stored payload cannot
    silently satisfy the next test's request — unit 23's point about shared
    state leaking between tests, applied to the one piece of shared state this
    file has.
    """
    _CACHE.clear()


# ==========================================================================
# Domain exception + handler
# ==========================================================================


class UpstreamError(Exception):
    """The one exception your service layer is allowed to raise.

    This is unit 23's domain exception, and it is the architectural point of
    the whole file, so it is worth being slow about.

    Notice what it carries: a `kind`, which is a short string naming what went
    wrong, and a `context`, which is usually the username or path involved. It
    does **not** carry a status code. That absence is deliberate. The moment a
    fetching function knows it should produce a 502, it has an opinion about
    HTTP, and it can no longer be reused by a script, a background worker, or
    a test — none of which have callers and none of which care what 502 means.
    Keeping HTTP out of the service layer is what lets the same code be driven
    by anything.

    kind in {"not_found","rate_limited","timeout","unavailable","bad_response"}.

    __init__(self, kind, context="") storing both as attributes.

    Write it as three lines: call super().__init__ with a readable message so
    the exception prints usefully in a traceback, then store kind and context
    as attributes, because the handler below reads both. A test constructs one
    directly and checks exc.kind and exc.context, so the attribute names are
    part of the contract.
    """

    # TODO


# The border post, in unit 23's phrase. Inside your program everybody speaks in
# kinds; outside, everybody speaks HTTP; this one function is the only place
# that knows both vocabularies. The service layer raises, this translates, and
# the mapping lives in exactly one place — so changing what a timeout looks
# like to your callers is a one-line change here rather than a hunt through
# every fetching function.
#
# The mapping itself is unit 22's argument in code. Their 404 is genuinely your
# caller's 404, so it passes through. Their 500 is a 502 from you, because a
# 500 from you would claim you are broken when you are not, and that sends the
# wrong on-call engineer looking in the wrong logs. A timeout is a 504, which
# says "slow" rather than "broken" — a different fix. And 429 propagates,
# because absorbing GitHub's throttling and continuing to hammer them on your
# caller's behalf is exactly the rudeness the throttle exists to stop.
#
# TODO: @app.exception_handler(UpstreamError) returning JSONResponse with
#       {"detail": ..., "kind": ...} and these statuses:
#         not_found 404 (detail f"not found: {context}")
#         rate_limited 429 ("upstream rate limited")
#         timeout 504 ("upstream timeout")
#         unavailable 503 ("upstream unavailable")
#         bad_response / anything else 502 ("upstream error")
#
# The `kind` goes into the body as well as deciding the status, so a caller can
# branch on a stable string instead of parsing your English. Note the "anything
# else" arm: an unrecognised kind must still produce a sensible response rather
# than falling through and becoming a 500.


# ==========================================================================
# Models
# ==========================================================================
#
# Every model below is an *output* shape — a description of what leaves your
# service. That is unusual, and it is worth noticing. In unit 21 you mostly
# wrote input models, which validate what arrives in a POST body and reject
# nonsense with an automatic 422. This service accepts no bodies at all: its
# only inputs are the path and the query string, and those are described by
# Query(...) on the dependencies and the handlers rather than by a model. So
# these seven classes all point outward.
#
# Which means the job they do here is different, and it is the fifth design
# decision. When you attach one as a route's `response_model`, FastAPI does two
# things. It documents the shape on /docs, so a caller can see every field and
# its type without asking you. And — the part that matters more — it *filters*
# what goes out: any field of your returned dictionary that the model does not
# declare is dropped before the response is serialised.
#
# Read that as a safety property rather than tidiness. GitHub's user payload is
# about thirty fields deep and includes an email address. You never wrote code
# to remove it; you simply never declared it, and so it cannot escape. The day
# an upstream starts including something it should not, a service that declares
# its responses is already not forwarding it, and a service that returns raw
# payloads has just leaked it. There is a test asserting exactly this, and its
# failure message says so.


class UserOut(BaseModel):
    """One GitHub user, slimmed to the six fields anyone actually wants.

    The output shape of GET /users/{username}, and also the `user` field
    nested inside a UserReport. `slim_user` below produces plain dictionaries
    in exactly this shape; this model is what declares and enforces it.

    Two of these fields do not exist upstream and are yours: `created_year`,
    which is the year pulled out of GitHub's `created_at` timestamp, and
    `profile_url`, which is their `html_url` renamed to something a caller can
    guess the meaning of. Deriving and renaming is a large part of what makes
    a gateway worth having.

    Both of those are optional because a sparse or unusual account may not
    have them, and a model that insists on a field the upstream sometimes
    omits turns a mildly odd user into a 500.

    login, name (str|None), followers int, public_repos int,
    created_year (int|None), profile_url (str|None).
    """

    # TODO


class RepoOut(BaseModel):
    """One repository, slimmed. The output shape of `slim_repo`.

    Appears inside RepoPage.items and inside UserReport.top_repos, which is
    the ordinary way models compose: define the small shape once and nest it
    wherever it belongs.

    Three fields here are optional and every one of them is optional for a
    real reason you will meet in the fixtures. A repository can have no
    language at all, no licence, and no push date if nobody has ever pushed to
    it. Unit 04's warning applies directly: the licence arrives as a nested
    object that is frequently null, so reaching into it needs care.

    name, stars int, forks int, language (str|None), archived bool,
    license (str|None), pushed (str|None).
    """

    # TODO


class RepoPage(BaseModel):
    """A page of repositories, plus the numbers a caller needs to page through.

    The output shape of GET /users/{username}/repos. It is an envelope: the
    repositories live under `items`, and the rest of the fields exist so the
    caller knows where they are.

    `total` is the count after filtering but *before* paging, and that is the
    field people get wrong. It is what tells a caller there are ninety more
    results waiting; if you set it to the length of `items` it always equals
    `count` and conveys nothing. `count` is how many you actually returned,
    which differs from `limit` on the last page.

    Echoing `limit` and `offset` back is a small courtesy that costs one line
    and saves a caller from having to remember what they asked for.

    username, total int, count int, limit int, offset int, items list[RepoOut].
    """

    # TODO


class LanguageStat(BaseModel):
    """One row of the language breakdown — a group-by result, essentially.

    If SQL is your background this is a `GROUP BY language` with a count, a
    sum, and a percentage of the whole. `language_breakdown` computes these;
    this model declares the row shape.

    `share` is stars in this language as a percentage of all stars, which is
    the number that makes the row interpretable — 160 stars means nothing on
    its own, 80% of everything they have means quite a lot.

    language str, repos int, stars int, share float  (percent of total stars, 1dp).
    """

    # TODO


class UserReport(BaseModel):
    """The whole report — the output shape of the endpoint worth demoing.

    This is the only response in the service that GitHub cannot give you, and
    that is the point of the endpoint: it combines a user payload and a
    repository list into one answer with analysis on top. `build_report`
    produces it as a plain dictionary; this model declares it and, via
    `response_model`, documents every field of it on /docs.

    Notice it nests. `user` is a UserOut, `languages` is a list of
    LanguageStat, `top_repos` is a list of RepoOut. Pydantic validates and
    filters all the way down, so an undeclared field cannot leak out of a
    nested object either.

    Two fields deserve a note. `mean_stars` and `median_stars` are both
    optional because a user with no repositories has no honest average — that
    is unit 01's divide-by-zero guard turning into a `None` in a response
    rather than a crash. And `skewed` is a derived flag rather than a raw
    number: when the mean sits well above the median, one runaway repository
    is dragging the average, and saying so in a boolean is more useful to a
    reader than making them compare two numbers themselves.

    user UserOut
    repo_count int
    total_stars int
    total_forks int
    mean_stars float | None      2dp
    median_stars float | None    2dp
    skewed bool                  mean > median * 1.2
    archived int
    licensed int
    languages list[LanguageStat]
    top_repos list[RepoOut]
    """

    # TODO


class ComparedUser(BaseModel):
    """One user's row in the comparison, with their position in the ranking.

    `rank` is 1-based — the top user is rank 1, not rank 0. Python counts from
    zero and humans do not, and this number is going into somebody's report,
    so convert at the boundary. It is a one-character detail that a test
    checks explicitly.

    login, followers int, public_repos int, rank int (1-based).
    """

    # TODO


class CompareOut(BaseModel):
    """The output shape of GET /compare, and the third design decision made visible.

    Look at `requested`, `found`, and `failed` sitting next to `users`. That
    trio is the whole partial-failure argument expressed as a response: you
    asked about five, four came back, here is the one that did not and why.
    A service that returned only the four would be quietly lying by omission;
    one that returned an error would have thrown away four good answers over
    one bad name.

    `failed` is a list of plain dictionaries rather than a model because its
    contents are diagnostic — a username and an error class name — and not
    something a caller should be building logic against.

    requested int, found int, failed list[dict], users list[ComparedUser],
    total_followers int.
    """

    # TODO


# ==========================================================================
# Dependencies
# ==========================================================================


async def get_client():
    """Yield an httpx.AsyncClient with TIMEOUT and HEADERS, closing it after.

    This is the most important five lines in the file, and it is worth
    understanding both halves of why.

    The `yield` makes it a **generator dependency**, unit 23's term for a
    dependency that hands over its value with `yield` rather than `return`.
    FastAPI runs everything above the yield on the way into your handler,
    passes you the client, lets the handler run, and then — after the response
    has been produced — comes back and runs everything below. Wrap the client
    in `async with` and its close is therefore guaranteed, whether the handler
    returned normally or blew up halfway through. Write `return
    httpx.AsyncClient(...)` instead and you get one client per request that is
    never closed, leaking connections quietly under load. Nothing in your
    tests will notice.

    The second half is why this exists as a function at all rather than as a
    module-level global. Being a dependency is precisely what lets the tests
    replace it: `test_service.py` writes
    `app.dependency_overrides[get_client] = override` and every route that
    declares `Depends(get_client)` silently receives a fake client returning
    canned responses instead. No monkeypatching, no "am I in test mode" flag,
    no conditional anywhere in this file. Your app does not know it is being
    tested; it asks for a client and takes whatever the current wiring hands
    it. That is the entire argument for dependency injection over a global,
    and it is why almost every test in the suite is possible.

    Set TIMEOUT and HEADERS on the client rather than on each call. The
    timeout in particular is not optional: without one, a GitHub that stops
    answering hangs your service, and your callers have their own timeouts and
    their own callers behind them.
    """
    # TODO
    raise NotImplementedError


def pagination(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """The paging parameters, declared once and reusable.

    A dependency function has a signature of its own, and FastAPI reads it
    exactly the way it reads a handler's — so these two `Query` declarations
    become real query parameters on any route that depends on this, complete
    with their ranges enforced and documented. Anything outside 1..100 or below
    zero gets an automatic 422 before your code is entered, which is unit 20's
    validation arriving for free.

    The value of putting them here rather than repeating them on each handler
    is that the rule lives in one place. Decide tomorrow that the maximum
    should be 200 and you change one number, and every endpoint and every line
    of the /docs page agrees.

    Just package the two values up and hand them back:

    -> {"limit": ..., "offset": ...}
    """
    # TODO
    raise NotImplementedError


# ==========================================================================
# Service layer -- raises UpstreamError, never HTTPException
# ==========================================================================


async def fetch(client, path, params=None, context=""):
    """The single place this service talks to GitHub.

    Everything upstream goes through here, which is what makes the error
    translation possible in one function instead of scattered through five.
    Its job is small: make the request, and turn every way `httpx` can fail
    into an `UpstreamError` with the right `kind`. It never raises
    HTTPException and never mentions a status code of its own — that is the
    handler's job, at the edge.

    GET {GITHUB}{path} -> parsed JSON, translating httpx errors.

    404 -> not_found, 429 -> rate_limited, other bad status -> bad_response,
    TimeoutException -> timeout, other RequestError -> unavailable.

    Two mechanical traps. `httpx.TimeoutException` is a *subclass* of
    `httpx.RequestError`, so the timeout branch has to come first or it will
    never be reached — unit 22 flagged this and it is a genuinely easy one to
    lose ten minutes to. And when you raise from inside an `except` block,
    write `raise UpstreamError(...) from exc`, so the traceback in your logs
    keeps the original httpx failure underneath yours with its real line
    number.

    `context` is whatever identifies the thing being fetched, usually the
    username. It travels with the exception so the 404 your caller receives
    can name what was missing rather than saying "not found" and stopping.
    """
    # TODO
    raise NotImplementedError


async def cached_fetch(client, key, path, params=None, context=""):
    """fetch(), memoized in _CACHE under `key` for CACHE_TTL_SECONDS.

    To memoize is to remember an answer you already computed and hand back the
    stored copy instead of doing the work again. For a gateway sitting in front
    of a rate-limited upstream this is not an optimisation, it is most of the
    reason to exist: a hundred callers asking about the same account within a
    minute have no business becoming a hundred requests to GitHub.

    The mechanic is unit 22's — `_CACHE` maps a key to `(fetched_at, payload)`,
    so "how old is this" is `time.time()` minus the stored timestamp. Under
    CACHE_TTL_SECONDS, return what you have and make no request at all. Over
    it, ignore the entry and fetch fresh. How long that TTL should be is the
    first of the five design decisions, and the trade-off runs between serving
    stale follower counts and burning through sixty requests an hour.

    A cache hit makes no request. Failures are never cached.

    That last sentence is the one with teeth, and there is a test for it. If
    you store the outcome of a failed fetch, you have pinned a failure in place
    for the whole TTL — every caller for the next minute gets the error and you
    never even retry. The fix is free if you write it in the right order: put
    the cache write strictly *after* the `await` that could raise, because a
    raised exception never reaches the next line.
    """
    # TODO
    raise NotImplementedError


async def get_user(client, username):
    """One user's raw payload, cached.

    A thin wrapper, and the thinness is deliberate: it fixes the path and the
    cache key in one place so that no caller has to remember either, and so
    that the report endpoint and the compare endpoint share cache entries
    rather than each keeping their own.

    Cached fetch of /users/{username}. Cache key f"user:{username}".

    The key format matters because /health reports the number of cached keys
    and a test counts them. Prefixing with the kind of thing being cached is
    what keeps `user:pallets` and `repos:pallets` from colliding.
    """
    # TODO
    raise NotImplementedError


async def get_repos(client, username):
    """One user's raw repository list, cached.

    Cached fetch of /users/{username}/repos with per_page=100.

    Cache key f"repos:{username}". Returns the raw list.

    `per_page=100` is GitHub's maximum, and asking for it means one request
    instead of four for a user with eighty repositories. Your own paging, in
    the /repos endpoint, then happens over the list you already hold — which
    is worth being clear about, because it means your `limit` and `offset` are
    yours and have nothing to do with GitHub's. Note also that this returns a
    list where get_user returns a dictionary; the analysis functions below
    depend on which is which.
    """
    # TODO
    raise NotImplementedError


async def get_many_users(client, usernames, concurrency=MAX_CONCURRENCY):
    """Fetch several users concurrently, bounded by a Semaphore.

    This is unit 22's fan-out — one request in, several requests out — and it
    is the engine behind /compare. Written as an ordinary loop, ten users at
    two hundred milliseconds each takes two seconds; started all at once with
    `asyncio.gather` it takes about as long as the slowest single one.

    Return (payloads, errors):
      payloads  raw user dicts that succeeded, in request order
      errors    [{"username": ..., "error": "<ExceptionClassName>"}, ...]

    One failure must not lose the others.

    There are three separate properties here and the tests check them
    separately, so build them one at a time.

    The first is concurrency: the requests must genuinely overlap, which means
    `asyncio.gather` rather than a loop with an `await` inside it.

    The second is surviving partial failure. By default `gather` raises the
    first exception it meets and discards every result that succeeded, which
    for a fan-out is almost always wrong — nine users came back fine and you
    would be throwing them away over one bad name. `return_exceptions=True`
    hands exceptions back to you as ordinary items in the results list
    instead, and you sort them apart with `isinstance(o, Exception)`. Because
    `gather` returns results in the order you passed the coroutines in rather
    than the order they finished, you can zip them back against `usernames`
    and know exactly which name each failure belongs to. The error entry
    records the exception's class name, which is `type(exc).__name__`.

    The third is respecting the cap. `asyncio.Semaphore(concurrency)` is a
    counter with a fixed number of tickets; a coroutine takes one on the way
    into `async with` and gives it back on the way out, so no more than
    `concurrency` requests are ever in flight however many you hand to
    `gather`. The fan-out stays concurrent, just five at a time instead of all
    at once. The test for this watches how many calls are simultaneously
    inside the fake client and asserts the peak never exceeds the cap, so a
    semaphore you create but never enter will fail it.
    """
    # TODO
    raise NotImplementedError


# ==========================================================================
# Pure analysis -- no network, no FastAPI
# ==========================================================================


def slim_user(payload):
    """Raw user dict -> the UserOut shape as a plain dict.

    GitHub sends about thirty fields about a user. You want six. This is the
    function that decides which, and it is the first half of the gateway's
    reason to exist — the response your callers see is one you designed rather
    than one GitHub designed.

    created_year from created_at[:4]; profile_url from html_url.
    Missing numbers become 0, missing strings become None.

    That last line is a policy, not a detail, and it is worth saying out loud
    in an interview. A missing follower count is genuinely zero followers, so
    zero is the honest answer and it keeps every sum downstream working. A
    missing name is not an empty name, it is *no name*, and `None` says so —
    unit 01's distinction between "nothing here" and "a value that happens to
    be empty," which is exactly the distinction a report reader needs.

    Take care with `created_at`: slicing the first four characters of a string
    is fine, slicing `None` is a crash, and a sparse fixture in the tests has
    no `created_at` at all.
    """
    # TODO
    raise NotImplementedError


def slim_repo(payload):
    """Raw repo dict -> the RepoOut shape as a plain dict.

    The same job as `slim_user`, one level messier, and the mess is the
    lesson.

    license comes from payload["license"]["name"] and is often null.
    pushed comes from pushed_at.

    Read that first line again, because it is unit 04's single most common
    runtime error waiting to happen. `payload["license"]` is not a missing
    key — it is a key that is present and holds `null`, and calling `.get()`
    on the result of it will not save you, because `None` has no methods. The
    fixtures contain a repository with exactly this shape precisely so you
    meet it. `(payload.get("license") or {}).get("name")` is the one-liner
    that survives both the missing key and the present-but-null case.

    Note the renames too: `stargazers_count` becomes `stars`, `forks_count`
    becomes `forks`, `pushed_at` becomes `pushed`. Shorter, consistent, and
    yours.
    """
    # TODO
    raise NotImplementedError


def language_breakdown(repos):
    """Slimmed repos -> list of LanguageStat dicts.

    A group-by, and if SQL is your background you already know the shape of
    the answer: one row per language, with a count of repositories, a sum of
    stars, and each language's share of the total. Unit 04's `setdefault`
    idiom is the three-line way to build the buckets.

    Note the input: this takes repos that have already been through
    `slim_repo`, so it reads `stars` and `language` rather than GitHub's
    field names. Keeping the slimming and the aggregating in separate
    functions means neither has to know about the other's problems.

    Repos with no language group under "unknown".
    share is that language's stars as a percentage of ALL stars, 1dp;
    0.0 when there are no stars at all.
    Sorted by stars descending, then language ascending.

    Three things there each have a reason. Bucketing null languages under
    "unknown" rather than dropping them keeps the shares adding up to 100 and
    stops a category quietly vanishing from the report. The zero-stars case is
    unit 01's divide-by-zero guard: a brand-new account with no stars anywhere
    would otherwise crash the whole endpoint, and 0.0 is the honest share. And
    the tiebreaker on the sort is what makes the output reproducible — without
    it two languages on equal stars come out in either order and the same
    correct report looks different on each run.
    """
    # TODO
    raise NotImplementedError


def build_report(user_payload, repo_payloads, top_n=5):
    """Assemble the whole UserReport as a plain dict.

    Pure: takes the two raw upstream payloads, returns data. This is where
    all the interesting logic lives, and it is testable with two hardcoded
    dicts and no network at all -- which is exactly the point.

    Sit with that word "pure" for a second, because it is the structural idea
    of the file. Two dictionaries go in, one dictionary comes out. There is no
    client in the signature, no `await`, no `Request`, no `HTTPException`,
    nothing imported from FastAPI. Everything difficult about this service —
    the averages, the median, the skew test, the grouping, the ranking — lives
    on this side of the line, where testing it costs a pair of hardcoded dicts
    and runs in a millisecond with the wifi off. Go and read
    `test_service.py`: the tests for this function are half a dozen lines each
    and they check real logic, while the tests for the endpoints mostly check
    plumbing.

    This is unit 06's fetch-and-transform split, which you first met on a
    single function, now applied at the scale of a whole service. It is the one
    structural habit most worth carrying into an interview, and it is worth
    naming when you do: *"the network is in three functions and everything
    else is pure, so all the logic is testable offline."*

    top_repos: the top_n by stars, ties broken by name ascending.

    Work in slimmed records — run both payloads through `slim_user` and
    `slim_repo` first, then compute over the clean shapes. Watch the empty
    case throughout: no repositories means no mean, no median, no languages
    and no top repos, and `None` rather than a crash is the answer in each
    place a division would have happened. A test builds the report for a user
    with zero repositories and then calls `json.dumps` on the result, which
    means every value you put in has to be plain JSON-serialisable data.
    """
    # TODO
    raise NotImplementedError


# ==========================================================================
# Endpoints
# ==========================================================================


# Six routes, and by the time you reach them almost nothing is left to do.
# Each one takes its client from Depends, calls the service layer, hands the
# result to a pure function, and returns a dictionary that a response_model
# then filters on the way out. If a handler here is growing logic, that logic
# probably wants to be a pure function above instead.


# GET /health  -> {"status": "ok", "cached_keys": <len(_CACHE)>}
#
#   This one takes no dependencies at all, and that is deliberate rather than
#   lazy. A health check exists so a load balancer, a container orchestrator or
#   a monitoring probe can ask "are you alive" every few seconds, and it must
#   be able to answer yes even when GitHub is on fire. Give it a client
#   dependency and you have built a health check that fails when your upstream
#   fails, which reports your service as dead when it is merely disappointed.
#   The cached-key count rides along because it costs nothing and it is the one
#   number that tells you at a glance whether your cache is doing anything.


# GET /users/{username}            response_model=UserOut
#
#   The simple one: fetch, slim, return. Worth building first because it
#   exercises the whole spine — the dependency, the cache, the error handler
#   and the response filter — in about four lines, so if anything is wired
#   wrongly you find out here rather than three endpoints later.


# GET /users/{username}/repos      response_model=RepoPage
#   Depends: get_client, pagination
#   Extra query params:
#       language str | None   exact, case-insensitive
#       min_stars int = 0     ge=0
#   Sort by stars desc, name asc. total is the count BEFORE paging.
#
#   Two dependencies on one route, which is the normal case: `pagination`
#   brings limit and offset with their ranges already enforced, and the two
#   filters here are declared inline because only this endpoint has them.
#   Case-insensitive means "python" must match "Python", so normalise both
#   sides before comparing rather than trusting the caller to match GitHub's
#   capitalisation. And keep the order straight — filter, then count for
#   `total`, then sort, then slice for the page. Counting after slicing is the
#   mistake that makes `total` useless.


# GET /users/{username}/report     response_model=UserReport
#   Fetch the user and the repos CONCURRENTLY (asyncio.gather), then
#   build_report. Query param: top int = 5, ge=1, le=20.
#
#   The endpoint worth demoing, and the only place in the file where the two
#   fetches are independent of each other — you do not need the user payload
#   in order to ask for the repositories, so there is no reason to wait for one
#   before starting the other. `asyncio.gather` starts both and returns when
#   the slower one lands, which roughly halves the time your caller waits.
#
#   That overlap is tested rather than assumed. `test_service.py` installs a
#   fake client with a fifty-millisecond delay on every call, times the
#   request, and asserts the whole thing finished in under ninety milliseconds
#   — which two sequential fetches cannot do. Write it as an ordinary
#   `await get_user(...)` followed by `await get_repos(...)` and the response
#   will be perfectly correct and the test will fail on the clock alone.
#
#   Everything after the gather is one call to `build_report`, because that is
#   where you put all the thinking.


# GET /compare                     response_model=CompareOut
#   Query param: users -- comma separated, 1..10 names after cleaning.
#   Outside that range -> 400 with a detail mentioning 10.
#   Users ranked by followers descending; rank is 1-based.
#
#   The fan-out endpoint. `get_many_users` does the concurrent work and hands
#   back both the payloads and the failures; this handler splits, ranks, and
#   counts.
#
#   "After cleaning" is doing real work in that specification. A caller who
#   sends `users=a,,b ` or `users= , ` has sent you whitespace and empty
#   strings, and those must be stripped out *before* you count — otherwise a
#   query of nothing but commas passes your check and you fan out to a list of
#   empty usernames. A test sends exactly that and expects a 400.
#
#   The cap of ten is the only place in the file you raise HTTPException
#   yourself rather than UpstreamError, and it is correct here: nothing went
#   wrong upstream, the caller asked for something you do not permit, and 400
#   is the status for that. Put the number in the detail message so the caller
#   learns the limit from the error rather than by guessing — a test asserts
#   "10" appears in it.
#
#   Rank is 1-based. Sort by followers descending and number from one.


# DELETE /cache -> {"cleared": <n>}
#
#   An operational endpoint: somewhere to go when you know the cache is stale
#   and you do not want to wait out the TTL. Return the number you removed
#   rather than an empty acknowledgement, so the caller can see whether
#   anything actually happened. DELETE is the right verb because the request is
#   idempotent — running it twice leaves the same state as running it once,
#   the second call simply reports zero.
