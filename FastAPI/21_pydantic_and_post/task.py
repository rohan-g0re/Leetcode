"""Unit 21 task — Pydantic models, POST, and response shaping.

You are building a small watchlist service. A caller can add a repository they
want to keep an eye on, list what they are watching, fetch one, change parts of
one, delete one, and ask for a summary. That is the whole product, and it is
enough to exercise every idea in the lesson.

There are two halves to the work and they are not equally hard. The first half
is four Pydantic models, and it is where the thinking is. The second half is six
endpoints, and once the models are right most of them are three or four lines,
because the models are already doing the parsing, the checking, and the shaping.
Write the models first. Run the model tests. Only then start on routes.

The data lives in a dictionary called `_STORE` that sits at module level and
survives between requests. Say plainly what that is: global mutable state in a
web application, which is normally a bad idea — it does not survive a restart,
it does not work at all once you run more than one worker process, and it makes
tests depend on each other unless you are careful. It is here for exactly one
reason, which is that swapping it for a real database is the one part of this
exercise that has nothing to do with FastAPI. Do not take it as a pattern. In
unit 25 you will put a proper store behind the same kind of endpoints.

The tests call reset_store() before and after each test to clear it out. That
function is provided, along with _STORE, _NEXT_ID and _new_id — you do not need
to change any of them.

Every model's docstring below lists its fields, types, defaults and constraints,
and every endpoint comment gives its method, path, status code and error
messages. Treat all of that as the specification rather than as description: the
tests assert on the exact field names, the exact key sets of each response, the
exact wording of the error details, and the exact sort order. If prose and a
listed detail ever seem to disagree, the listed detail wins.

Run:  python -m pytest test_task.py -v
      uvicorn task:app --reload      then open /docs and POST something
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Watchlist", version="1.0.0")


# In-memory store: id -> stored dict. Provided for you.
_STORE: dict[int, dict] = {}
_NEXT_ID = {"value": 1}


def reset_store():
    """Clear the store. Used by the tests; provided for you."""
    _STORE.clear()
    _NEXT_ID["value"] = 1


def _new_id():
    """Hand out the next id. Provided for you."""
    value = _NEXT_ID["value"]
    _NEXT_ID["value"] += 1
    return value


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------


class WatchIn(BaseModel):
    """What a caller may POST — the in-model.

    This is the contract for incoming data. Anything that does not satisfy it
    never reaches your endpoint; FastAPI rejects the request with a 422 that
    names the offending field, and your handler is not called at all.

    Fields, with their types, defaults and constraints:

      name      str            required, 1..100 characters
      owner     str            required, 1..100 characters
      stars     int            default 0, must be >= 0
      language  str | None     default None
      tags      list[str]      default empty list
      notes     str | None     default None, max 500 characters

    `name` and `owner` are required because they have no default. The other
    four have defaults, so a caller may leave them out. Remember that `tags`
    needs `default_factory` rather than a bare `[]` — that is unit 06 and unit
    10's mutable-default trap for the third time, and one of the tests builds
    two models and checks that appending to one's tags leaves the other's
    empty.

    Two validators to add, both on this model:

      - `name` must not contain a space. Raise
        ValueError("name must not contain spaces") when it does. Otherwise
        store it LOWERCASED, so "FlAsK" becomes "flask".

      - `tags` are lowercased, stripped of surrounding whitespace,
        de-duplicated, and returned in sorted order. A tag that is empty or
        contains only whitespace is dropped entirely. So
        ["  Web ", "web", "API", "", "  "] becomes ["api", "web"].

    Both of those must RETURN the value they want stored. That is the rule from
    the lesson worth repeating here, because forgetting it does not raise an
    error — the field is silently set to None and you spend twenty minutes
    wondering where your data went. The `tags` validator rejects nothing at
    all; it exists purely to normalize, which is a perfectly good reason for a
    validator to exist.
    """

    # TODO


class WatchOut(BaseModel):
    """What callers get back — the out-model.

    Seven fields:

      id, name, owner, stars, language, tags, full_name

    `full_name` is the string "<owner>/<name>", so a repo owned by "pallets"
    and called "flask" has the full name "pallets/flask". It is computed by the
    endpoint when it builds the response, not stored in _STORE. There is no
    reason to keep a value on disk that you can always derive from two values
    you already have.

    Now look at what is NOT in that list: `notes`. It is accepted on input by
    WatchIn, it is written into _STORE, and it is never returned by anything.
    That asymmetry is the entire reason in-models and out-models are separate
    models rather than one shared one, and it is the idea from this unit most
    worth being able to explain out loud. The store keeps everything; the
    caller sees a curated subset; the decision about which fields those are
    lives in exactly one place, this class.

    Several tests exist purely to prove `notes` never leaks — from POST, from
    the list endpoint, from PATCH, from the `top` entry inside the stats
    response, and one that reads /openapi.json and checks that `notes` is not
    even documented as an output field. If you find yourself deleting `notes`
    from a dict somewhere in an endpoint, stop: `response_model` already does
    that, everywhere, for free.
    """

    # TODO


class WatchPatch(BaseModel):
    """A partial update. EVERY field is optional.

      stars     int | None      >= 0 when a value is given
      language  str | None
      tags      list[str] | None
      notes     str | None      max 500 characters

    Note that "optional" means "you may omit it", not "anything goes" — the
    constraints still apply to any value that IS supplied, so a PATCH sending
    stars = -5 must still be rejected with a 422.

    The interesting part is what the endpoint has to do with this. A field the
    caller omitted must leave the stored value alone. A field the caller
    explicitly set to null must clear the stored value. Those are two different
    intentions and the service has to honour both:

      {"stars": 99}                      -> set stars, do not touch language
      {"stars": 99, "language": null}    -> set stars, AND clear language

    Reading `patch.language` cannot tell those apart, because in both cases it
    holds None — once because that is the default and once because the caller
    asked for it. A plain model_dump() cannot tell them apart either; it dumps
    every field including the untouched defaults, so using it would overwrite
    every omitted field with None. Pydantic does track which fields were
    actually present in the incoming data. Find the model_dump argument that
    filters the dump down to just those, and the whole of PATCH becomes one
    update line with no conditionals in it.
    """

    # TODO


class WatchStats(BaseModel):
    """Summary response over everything currently in the store.

      count            int
      total_stars      int
      mean_stars       float | None      2dp, None when the store is empty
      languages        dict[str, int]    language (or "unknown") -> count
      top              WatchOut | None   the most-starred entry, None when empty

    Two things to notice. `mean_stars` is None rather than 0 for an empty
    store, because the mean of nothing has no honest answer — unit 01's
    divide-by-zero guard, showing up in a response shape. And `top` is a
    WatchOut nested inside another model, which means it is validated and
    filtered exactly like any other WatchOut. That is why `notes` cannot leak
    through the stats endpoint either, without you writing a line to prevent
    it.

    An entry with no language counts under the key "unknown". Note the store
    holds the language exactly as the caller sent it, so "Python" stays
    "Python" here — only `name` gets lowercased, by its validator.
    """

    # TODO


# --------------------------------------------------------------------------
# Endpoints
# --------------------------------------------------------------------------


# Helper you will want. Turns a stored dict into the response shape.
def to_out(stored):
    """Build the WatchOut payload for one stored record.

    Every endpoint that returns a watchlist entry needs the same conversion:
    take the dict sitting in _STORE and produce the seven keys WatchOut
    declares — id, name, owner, stars, language, tags, full_name — with
    full_name built from owner and name.

    Return a plain dict rather than a WatchOut instance. That is not a
    compromise; `response_model` validates whatever the endpoint hands back, so
    a dict with the right keys is checked just as thoroughly as an instance
    would be, and building one is less ceremony. Write this once and every
    endpoint below gets shorter.
    """
    # TODO
    raise NotImplementedError


# POST /watch          status 201, response_model=WatchOut
#   Takes a WatchIn as the request body. Because the parameter is annotated
#   with a model, FastAPI knows the data comes from the body, parses it,
#   validates every field, and only then calls your function -- so there is no
#   checking left for you to do at the top of the handler.
#
#   Assign an id with _new_id(), store the whole record in _STORE (including
#   notes -- it is kept internally, and response_model is what stops it going
#   back out), and return the WatchOut shape.
#
#   Conflict: if the store already holds an entry with the same owner/name
#   pair, compared case-insensitively, raise a 409 whose detail is exactly
#   "already watching: <owner>/<name>". Do this check before assigning an id,
#   so a rejected request does not burn one.


# GET /watch           response_model=list[WatchOut]
#   Returns everything in the store, filtered and sorted. These are query
#   parameters, so they are declared as scalars -- same constraint vocabulary
#   as Field, just attached with Query:
#
#     language   str | None    exact match, case-insensitive; omitted means
#                              no language filter at all
#     min_stars  int = 0       ge=0
#     limit      int = 50      ge=1, le=200
#
#   Sort by stars descending, then by name ascending as the tie-break. The
#   tie-break is not decoration: without it two entries on the same star count
#   could come back in either order and the same request would produce a
#   different answer on different runs.
#
#   Apply the limit after sorting, so `limit` gives you the top N rather than
#   an arbitrary N.


# GET /watch/{item_id} response_model=WatchOut
#   Fetch one entry by id. When the id is not in the store, raise a 404 whose
#   detail is exactly "not found: <id>".
#
#   Note that item_id is annotated as an int, which means a request for
#   /watch/abc is rejected with a 422 before your function runs -- you never
#   have to check that the id is a number.


# PATCH /watch/{item_id}   response_model=WatchOut
#   Two parameters from two different places: item_id is a scalar matching the
#   path placeholder, so it comes from the path, and the WatchPatch parameter
#   is a model, so it comes from the body.
#
#   Apply ONLY the fields the caller actually sent. An omitted field must not
#   overwrite the stored value with None; an explicitly null field must set it
#   to None. See the WatchPatch docstring for the tool that distinguishes them.
#   An empty body must change nothing at all.
#
#   404 with the same "not found: <id>" detail when the id does not exist.


# DELETE /watch/{item_id}  status 204
#   Remove the entry and return no body. 204 means "done, and there is
#   deliberately nothing to send back", and the body must be genuinely empty --
#   not null, not {}. The test asserts the response content is b"".
#
#   404 with the same "not found: <id>" detail when the id does not exist.


# GET /watch-stats     response_model=WatchStats
#   Summary over everything in the store, in the WatchStats shape.
#
#   Handle the empty store first and return the all-zero shape: count 0,
#   total_stars 0, mean_stars None, languages {}, top None. response_model
#   validates that too, so the keys have to match WatchStats exactly.
#
#   Otherwise: count the records, total their stars, take the mean rounded to
#   two decimal places, count records per language (with "unknown" for records
#   that have none), and put the highest-starred entry in `top` as a WatchOut
#   payload. `top` uses the same ranking as GET /watch -- stars descending,
#   name ascending -- so if you pulled that sort into a small helper, reuse it
#   here.
