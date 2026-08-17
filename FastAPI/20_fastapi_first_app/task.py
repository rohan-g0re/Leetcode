"""Unit 20 task — your first FastAPI app.

You are building a small read-only web service over the GitHub repositories
fixture. Nothing here touches the network: the data is loaded from a file on
disk once, at import time, into the `REPOS` list. That is deliberately how you
would prototype a service in front of an interviewer — get the shape of the API
right against fixed data first, and wire the real upstream in afterwards, once
the routes and the response shapes have stopped moving.

This task file is shaped differently from every other one in the course. There
are no function stubs waiting for you. Instead there is a block of comments
below, one per endpoint, and each of those comments is the specification for a
route you have to write from scratch — decorator, function, and body. Seven
routes in total. Read the whole block before you write any of it, because the
ORDER you declare two of them in changes whether they work at all.

Everything above the comment block is provided and needs no edits. `load_repos`
reads the fixture and flattens each repository down to seven fields; `REPOS` is
the resulting list of flat dictionaries, which is unit 04's target shape and is
exactly what your handlers will be filtering, sorting, and returning.

Every handler here should be a plain `def`, not `async def` — nothing in this
service waits on anything, since the data is already in memory.

Run the tests:   python -m pytest test_task.py -v
Run the server:  uvicorn task:app --reload
                 then open http://127.0.0.1:8000/docs

The tests use `fastapi.testclient.TestClient`, which calls your app
in-process — no server started, no port opened, no network involved. It builds
the request object, hands it straight to the app, and gives you back the
response. That is how APIs are tested, and it is why `pytest` works here
without you running uvicorn first.

Once the tests are green, do start uvicorn and open /docs. Every constraint you
declared shows up there as a documented, clickable input box, and clicking
"Try it out" is the demo worth showing someone.
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Path as PathParam, Query

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"

app = FastAPI(
    title="Repo Explorer",
    description="A tiny read-only API over a snapshot of GitHub repositories.",
    version="1.0.0",
)


def load_repos():
    """Load and slim the repo fixture. Provided for you -- no TODO here.

    Returns a list of dicts with keys:
        name, language, stars, forks, open_issues, archived, license
    """
    raw = json.loads(
        (FIXTURES / "github_repos_pallets.json").read_text(encoding="utf-8")
    )
    return [
        {
            "name": repo["name"],
            "language": repo.get("language"),
            "stars": repo.get("stargazers_count") or 0,
            "forks": repo.get("forks_count") or 0,
            "open_issues": repo.get("open_issues_count") or 0,
            "archived": bool(repo.get("archived")),
            "license": (repo.get("license") or {}).get("name"),
        }
        for repo in raw
    ]


REPOS = load_repos()


# --------------------------------------------------------------------------
# TODO: build the seven endpoints specified below.
#
# Each one is an ordinary Python function with a decorator above it. The
# decorator registers the function as the handler for that method and path;
# the function does the work and returns a dictionary or a list, which FastAPI
# turns into JSON for you. There is no serializer to call anywhere in here.
#
# Read the whole block before you write anything. The order in which you
# declare /repos/top and /repos/{name} decides whether /repos/top works, and
# that is explained where those two routes appear.
#
# Four of these routes sort repositories the same way — stars descending, then
# name ascending, so that repositories with equal star counts come out in a
# stable, predictable order rather than shuffling between runs. Writing that
# ordering once as a small helper function and calling it from each route will
# save you repeating yourself and getting one of them subtly wrong.
# --------------------------------------------------------------------------


# GET /health
#
#   -> {"status": "ok", "repos": <number of repos loaded>}
#
#   Start here, because it is the shortest route you will ever write and it
#   proves your app, your decorator, and your server are all wired up before
#   you write anything with logic in it.
#
#   It is also the endpoint every deployed service is expected to have, and
#   its absence gets noticed. A load balancer — the machine that spreads
#   incoming traffic across several copies of your service — hits an endpoint
#   like this every few seconds on every copy, and stops sending traffic to
#   any copy that fails to answer. Monitoring systems do the same to decide
#   whether to wake somebody up. The point is that it is cheap: it takes no
#   parameters, touches no upstream, and answers instantly, so a failure to
#   respond genuinely means the process is dead rather than merely busy.
#
#   Reporting the repo count alongside "ok" is a small extra: it shows the
#   data actually loaded, not just that Python is running.


# GET /repos
#
#   The main listing endpoint: filter, sort, and page through the repos.
#
#   Query parameters, all of them optional:
#
#       language   str  | None   exact match on the repo's language, but
#                                case-INSENSITIVE, so "python" must match
#                                repositories whose language is "Python".
#                                None means "do not filter on language".
#       min_stars  int  = 0      keep repos whose stars are >= this value.
#                                Must be >= 0.
#       archived   bool | None   None means "do not filter on it". Note that
#                                False is NOT the same as None here: False
#                                means "only the repos that are not archived".
#                                A truthiness check collapses those two cases
#                                together, so test against None explicitly.
#       limit      int  = 10     how many rows to return. Between 1 and 100.
#       offset     int  = 0      how many rows to skip before returning any.
#                                Must be >= 0.
#
#   Apply the filters, then sort by stars descending and name ascending, and
#   only THEN apply offset and limit. Sorting before paging is what makes page
#   two contain the rows that genuinely come after page one; sort afterwards
#   and each page is merely sorted within itself, which is a real and
#   surprisingly common bug.
#
#   Respond with:
#
#   {
#     "total": <matches before paging>,
#     "count": <rows actually returned>,
#     "limit": ..., "offset": ...,
#     "items": [ <repo dicts> ]
#   }
#
#   "total" and "count" are deliberately two different numbers and both are
#   needed. "total" is how many repos matched the filters; "count" is how many
#   rows are in "items" after the offset and limit were applied. With the
#   defaults against this fixture, total is 17 and count is 10. That gap is
#   what makes a paged response honest — the caller can see there is more to
#   fetch, and can work out how many pages remain without guessing. It is the
#   same distinction the paginators in unit 15 cared about when you were on
#   the consuming side of it, and now you are the one who has to publish it.
#
#   An offset past the end of the results is not an error: total stays the
#   same, count is 0, and items is empty. Python slicing gives you that for
#   free rather than raising, so it needs no special case.
#
#   Declare the numeric parameters with Query(...) and ge/le bounds, so that
#   an out-of-range value produces a 422 with a precise message instead of
#   quietly doing something strange. A limit of 0, a limit of 101, a negative
#   limit, a negative offset, a negative min_stars, and a limit of "many" must
#   all be rejected — and you should be writing zero lines of validation code
#   to make that happen.


# GET /repos/top
#
#   Query parameter: n int = 3, between 1 and 20
#
#   -> a LIST of the n most-starred repos, as bare repo dicts with no wrapper
#      around them. Ties are broken by name ascending, the same ordering
#      /repos uses.
#
#   This route MUST be declared BEFORE /repos/{name}. Here is why, because it
#   is worth understanding rather than memorising.
#
#   FastAPI keeps your routes in a list, in the order the decorators ran —
#   which is top to bottom through this file. When a request arrives it walks
#   that list from the start and uses the FIRST route that matches. It does
#   not collect every match and pick the most specific one. So /repos/{name}
#   matches any single segment after /repos/, and the literal text "top" is a
#   single segment. Declared first, it wins: your name-lookup handler is
#   called with name="top", finds no repository called that, and raises a 404
#   from code that looks perfectly correct.
#
#   One of the tests exists purely to catch this. If it fails, the problem is
#   never your ranking logic — it is the order these two appear in the file.


# GET /repos/{name}
#
#   `name` here is a PATH parameter: it appears in braces in the path, so
#   FastAPI fills it from that segment of the URL rather than from the query
#   string.
#
#   Match it against the repo name exactly, but case-insensitively, so that
#   /repos/FLASK finds the repository named "flask".
#
#   -> the repo dict itself, not wrapped in anything
#   -> 404 when there is no match, with the detail string in exactly this
#      form:  "repo not found: <name>"
#      where <name> is the name the caller actually asked for. Echoing it
#      back matters: a caller debugging a batch of a thousand requests learns
#      nothing from a bare "not found".
#
#   Produce that 404 by RAISING HTTPException, not by returning it. Returning
#   it hands FastAPI an object to serialize and sends it with status 200 — a
#   successful response whose body merely describes a failure, with nothing to
#   warn you. If a 404 test is somehow getting a 200, this is why.


# GET /languages
#
#   -> a LIST of {"language": ..., "repos": ..., "total_stars": ...}
#
#      one entry per language, where "repos" is how many repositories use it
#      and "total_stars" is their stars added up. Sorted by total_stars
#      descending, then language ascending.
#
#      Repositories whose language is None are grouped together under the
#      literal string "unknown" rather than being dropped. Dropping them would
#      make the per-language counts stop adding up to the total number of
#      repos, and one of the tests checks exactly that they still do.
#
#   This is SQL's GROUP BY done by hand: accumulate into a dictionary keyed by
#   language as you walk the repos once, then sort the collected entries at
#   the end. Unit 04's setdefault idiom is the shape you want.


# GET /stats
#
#   One summary object for the whole collection.
#
#   -> {
#        "repos": <count>,
#        "total_stars": <sum>,
#        "mean_stars": <rounded to 2dp>,
#        "median_stars": <rounded to 2dp>,
#        "archived": <count of archived repos>,
#        "licensed": <count with a non-null license>,
#        "languages": <count of distinct non-null languages>,
#      }
#
#   Note that "languages" counts DISTINCT non-null languages, so it does not
#   include the "unknown" bucket that /languages reports — which is why the
#   two endpoints deliberately disagree by one.
#
#   Worth looking at the two averages once you have them. The mean is around
#   6919 and the median is 167, because one repository holds most of the stars
#   in the entire fixture. That is a heavily skewed distribution, and quoting
#   the mean on its own would be misleading. Reporting both, and saying out
#   loud why they differ, is the kind of remark that lands well in an
#   interview.


# GET /search
#
#   Query parameter: q str, REQUIRED, between 2 and 50 characters.
#
#   Case-insensitive substring match on the repo name — "fla" finds "flask".
#
#   -> {"q": <the query>, "count": n, "items": [...]}
#
#   No matches is a perfectly good answer, not an error: count 0, items empty,
#   status 200.
#
#   All three of the failure cases the tests check — q missing entirely, q too
#   short, q too long — come free from a single declaration:
#
#       q: str = Query(min_length=2, max_length=50)
#
#   No default means required, so a missing q is a 422. The two length bounds
#   give you the other two 422s. You write no validation code by hand, and all
#   three rules show up in /docs as documented constraints on the input box.
#   Compare that against validate_page_size in unit 08, which was the same
#   idea written out longhand.
