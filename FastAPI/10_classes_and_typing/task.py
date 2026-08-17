"""Unit 10 task — classes and type hints.

You build two things here, and they are deliberately different in character.

The first is a `Repo` dataclass, together with the two conversions that
surround it: raw API dictionary in, plain dictionary out. That sandwich —
messy JSON, tidy typed object, tidy dictionary — is exactly what Pydantic does
for you in unit 21. Doing it by hand once means that when Pydantic does it
automatically, you will know precisely what it took off your hands.

The second is a small `ApiClient` class that holds configuration a caller would
otherwise have to repeat on every single request. It makes no network calls;
it only pretends to. But it is the shape of a real client wrapper, and unit 15
turns this exact design into a live one.

This task file is laid out slightly differently from the others. Two of the
four TODOs sit inside a class body rather than inside a function, and for those
two the specification lives in the class docstring above them. Read the whole
docstring before you start typing — it lists every field and every method you
are expected to produce.

Annotate every function and method you write with type hints. They change
nothing about how your code runs, which is the point of the lesson; write them
anyway, because it is the habit Part 4 depends on.

Run:  python -m pytest test_task.py -v
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


@dataclass
class Repo:
    """One GitHub repository, reduced to the seven fields we care about.

    Fill in the field list and then the methods. The two TODO comments below
    mark where each half goes.

    Required fields (no default):   name, owner
    Optional fields (with default): language=None, stars=0, forks=0,
                                    license=None, topics=<empty list>

    Every field needs a type annotation, because that annotation is how the
    @dataclass decorator finds it. A line without one is invisible to it and
    simply will not become a field. Fields that can hold nothing are written
    `str | None`, which reads as "text, or None".

    Two rules the lesson covered, both of which Python will stop you on:

      * Required fields must come first. A field with a default cannot sit
        above one without, because the generated __init__ would end up with a
        required parameter after an optional one.

      * `topics` is a list, and a list default written directly in the class
        body would be created once and then shared by every Repo you ever
        build. Appending to one repo's topics would silently change all of
        them. Dataclasses refuse to let you do it, which is why `field` is
        imported at the top of this file — use it with the argument that hands
        over a way of *making* a fresh empty list rather than a list itself.
        There is a test that builds two repos, appends to one, and checks the
        other is untouched.

    Methods to write:

      is_popular(threshold=1000) -> bool
          True when stars >= threshold.

      summary() -> str
          "flask (Python): 66000 stars"
          When language is None, use "unknown":
          "meta (unknown): 100 stars"

    Remember that a method's first parameter is `self`, the instance it was
    called on, and that reaching a field means writing `self.stars` rather than
    a bare `stars`. If you forget `self` you get a TypeError complaining about
    argument counts that look off by one — that is the error, not a mystery.

    You do not write __init__, __repr__, or __eq__. The decorator generates all
    three from your field list, and the tests exercise all three.
    """

    # TODO: fields
    # TODO: methods


def repo_from_api(raw: dict[str, Any]) -> Repo:
    """Build a Repo from one raw GitHub API repo dict.

    This is the messy half of the sandwich: a genuine API record goes in, a
    clean typed object comes out. The mapping is the same one you did in unit
    09's slim_repos, so the shape should be familiar.

    Mapping (same as unit 09's slim_repos):
      name     <- raw["name"]
      owner    <- raw["owner"]["login"]        (nested; may be absent)
      language <- raw["language"]              (often null)
      stars    <- raw["stargazers_count"]      (default 0 if absent)
      forks    <- raw["forks_count"]           (default 0 if absent)
      license  <- raw["license"]["name"]       (raw["license"] is often null)
      topics   <- raw["topics"]                (default [] if absent or null)

    Must not raise on any record in the fixture file.

    That last line is the actual difficulty, and it is worth taking seriously
    rather than discovering the hard way. The fixture is real GitHub data, and
    real GitHub data has holes in it. Some of those repositories have no
    licence, and the way that arrives is not a missing key — the key is present
    and holds null, which Python reads as None.

    So `raw.get("license", {})` is not enough. A default only applies when the
    key is absent, and here the key is right there holding nothing, so .get()
    dutifully hands you None and the next lookup on it explodes with
    "'NoneType' object is not subscriptable". Unit 04's `or {}` handles both
    cases at once, because None is falsy. The same reasoning applies to
    `topics`, where you want an empty list rather than an empty dict, and to
    the two counts, where you want a zero.

    One record failing must not be allowed to kill a run that has already
    processed sixteen others. Write it so nothing in the file can trip it.
    """
    # TODO
    raise NotImplementedError


def repo_to_dict(repo: Repo) -> dict[str, Any]:
    """Convert a Repo back into a plain dict, ready for json.dumps or pandas.

    Keys: name, owner, language, stars, forks, license, topics.

    This is the other end of the sandwich. The dataclass was a comfortable
    place to hold the data while you worked on it; a plain dictionary is what
    everything downstream actually wants — json.dumps, pandas, and eventually
    a FastAPI response. Unit 04 called this shape the target, and it still is.

    There is a one-line way to do this for dataclasses. Find it in the
    dataclasses module rather than writing the dict out by hand.

    The function you are looking for takes an instance and gives back a
    dictionary whose keys are the field names, in the order you declared them.
    `help(dataclasses)` in the interactive prompt will show you the whole
    module in about ten seconds. Writing the seven keys out by hand also passes
    the test, but it means editing this function every time the dataclass gains
    a field, which is exactly the kind of duplication the tool exists to remove.
    """
    # TODO
    raise NotImplementedError


def load_repos() -> list[Repo]:
    """Load fixtures/github_repos_pallets.json and return a list of Repo objects.

    Read the file, parse the JSON into Python, and turn each raw record into a
    Repo using the function you just wrote. The FIXTURES constant at the top of
    this file already points at the right directory, so build the path from it
    rather than hard-coding one — a relative path would break the moment the
    tests were run from a different working directory.

    Unit 09 covered the reading and parsing. The result is a list of Repo
    objects, not a list of dictionaries, and the test checks how many there are
    and adds up their stars.
    """
    # TODO
    raise NotImplementedError


class ApiClient:
    """A tiny stand-in for a real HTTP client.

    Holds shared configuration so callers don't repeat it on every request --
    the same job requests.Session does, which you meet in unit 15.

    Everything below goes under the single TODO at the bottom of this
    docstring. Nothing here touches the network; `request` only builds a
    dictionary describing the call it would have made, which keeps the exercise
    about class mechanics rather than about HTTP.

    Construction:
        ApiClient("https://api.github.com")
        ApiClient("https://api.github.com/", token="abc", timeout=5)

    Requirements:

      __init__(self, base_url, token=None, timeout=10)
          Store base_url with any trailing "/" removed.
          Store token and timeout.
          Start a call counter at 0.

      DEFAULT_HEADERS  (a CLASS attribute, shared by all instances)
          {"Accept": "application/json"}

      headers property or method -> dict
          Make it a method called `headers()`. Returns a NEW dict combining
          DEFAULT_HEADERS with an "Authorization" entry of
          f"Bearer {token}" -- but only when a token was given.
          Calling it must never modify DEFAULT_HEADERS. Check the test.

      url(*parts) -> str
          Join base_url and the parts with single slashes.
          client.url("users", "torvalds") -> "https://api.github.com/users/torvalds"
          client.url() -> "https://api.github.com"

      request(path_parts) -> dict
          The fake "call". Increment the counter and return
          {"url": <the built url>, "timeout": <timeout>, "headers": <headers()>}
          path_parts is a list/tuple of segments.

      __repr__
          "ApiClient(base_url='https://api.github.com', calls=0)"

    Notes on the parts that are easy to get subtly wrong:

      DEFAULT_HEADERS is written directly in the class body rather than in
      __init__, and that makes it a class attribute: one dictionary, created
      once, shared by every ApiClient that will ever exist. Read it through
      `self.DEFAULT_HEADERS` and it works fine. The danger is writing to it.
      If `headers()` adds an "Authorization" key to that dictionary, it has not
      added a header to this client — it has permanently rewritten the default
      for every client in the program, including ones created later and ones
      belonging to entirely different code. There is a test that calls
      `headers()` with a token and then checks the class attribute is still
      exactly `{"Accept": "application/json"}`. The fix is one word long and
      involves not modifying the original at all; unit 04 mentioned two ways of
      producing a separate dictionary with the same contents.

      The call counter goes in __init__ for the same reason, from the other
      side: each client needs its own, and a test builds two clients, makes a
      request on one, and checks the other still reads zero.

      `url(*parts)` uses unit 06's star syntax, which collects however many
      arguments you were given into a tuple. Zero parts is a real case — the
      test calls `client.url()` and expects the base URL back with no trailing
      slash, which is why __init__ strips one off.

      __repr__ is the dunder the lesson told you always to write. The expected
      string quotes the URL, which is what the `!r` conversion inside an
      f-string gives you.
    """

    # TODO
