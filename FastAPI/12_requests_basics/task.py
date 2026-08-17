"""Unit 12 task — calling real APIs with requests.

Eight functions that together form a complete, small program: it takes a
GitHub username, fetches that user and their repositories over the real
internet, and hands back one tidy report dictionary. That is the exact shape
of the thing an interviewer is likely to ask you for, so build it once here
where nobody is watching.

Work through them in order. The first two are the plumbing you will type from
memory forever afterwards. The middle ones are the judgment calls. The last
three are pure logic with no network in them at all, and they are where the
interesting bugs live.

The tests come in two flavours:

  * offline  - a fake requests.get is patched in, so the logic is checked
               without touching the network
  * live     - marked @pytest.mark.live, these hit api.github.com for real

    python -m pytest test_task.py -v -m "not live"    # offline only
    python -m pytest test_task.py -v                  # everything

That word "patched" is worth understanding, because it explains a design
choice in these functions. The offline tests replace `requests.get` with a
fake function of their own that returns a canned response instead of calling
out to the internet. They can do that because your code looks `requests.get`
up by name at the moment it calls it, rather than holding on to its own
private copy — so swapping out that one attribute swaps it out for everything
below. This is why the functions here call `requests.get` directly instead of
each building a client object of their own, and it is why the whole file can
be tested in a fraction of a second with no network at all.

GitHub allows 60 unauthenticated requests per hour per IP. The live tests use
about six. Don't run them in a loop — burn the allowance and you are locked
out for the rest of the hour.

Run the file directly to see it work against the real API:
    python task.py torvalds
"""

import json
import sys

import requests

BASE = "https://api.github.com"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 10


def fetch_json(url, params=None, timeout=TIMEOUT):
    """GET `url` and return the parsed JSON body.

    Make the request, check that the server was happy with it, and hand back
    the body as Python dictionaries and lists. Nothing more.

    Requirements:
      - send HEADERS
      - pass params straight through to requests (do NOT build a query string)
      - pass the timeout
      - call raise_for_status() so 4xx/5xx become exceptions
      - return the parsed JSON

    Four lines. This is the function you will type in the first minute of the
    interview, so type it here until it is automatic.

    Each of those four requirements is a decision from the lesson, and it is
    worth naming them as you type. HEADERS goes on because GitHub returns 403
    to a request with no User-Agent. The params go through the `params=`
    argument rather than into an f-string, because requests percent-encodes
    them correctly and drops the None ones. The timeout goes on because
    requests has no default and a silently stalled server would hang you
    forever with no error at all. And raise_for_status() goes on so that a
    404 or a 500 becomes an exception here, rather than an error page that
    parses cleanly and gets treated as real data three lines later.

    Notice what this function does not do: it does not catch anything. A
    failure propagates — it travels straight up to whoever called this — and
    that is deliberate, because fetch_json has no idea whether its caller
    wants to abort, retry, or carry on without that record. Deciding is the
    caller's job. `safe_fetch`, next, is the caller that decides.
    """
    # TODO
    raise NotImplementedError


def safe_fetch(url, params=None):
    """Like fetch_json, but never raises. Returns a (data, error) tuple.

    Do the same fetch, but instead of letting a failure escape, catch it and
    describe it. The caller always gets back a pair of values, and exactly one
    of the two is filled in.

    On success:  (data, None)
    On failure:  (None, "<short error description>")

    The error string must start with the exception's class name, e.g.
    "HTTPError: 404 Client Error: ..." or "ConnectionError: ...".

    Catch requests.RequestException -- one handler covers timeouts,
    connection failures, HTTP errors, and JSON decode failures.

    That single except clause is the exception hierarchy from the lesson
    paying off. Timeout, ConnectionError, HTTPError, TooManyRedirects and
    JSONDecodeError are all children of RequestException, and unit 08 taught
    you that catching a parent catches every one of its children. So one
    handler covers every way a network call can go wrong, and you do not have
    to enumerate them or guess which you forgot.

    Returning the error rather than printing it lets the caller decide what
    to do: warn, skip the record, or abort the run.

    That (data, error) shape should look familiar — it is unit 08's
    parse_records returning (good, failures) wearing different clothes, and
    for the same reason. Printing the problem buries it in a log nobody reads
    and gives the caller nothing to branch on. Raising it forces the caller to
    care, even when they would rather carry on. Handing the failure back as an
    ordinary value lets them choose, and you will see exactly that choice made
    in `user_report` at the bottom of this file.

    You should not repeat the request code here. Call fetch_json and wrap that
    call in the try.
    """
    # TODO
    raise NotImplementedError


def describe_response(response):
    """Summarize a Response object without assuming anything about it.

    This is the "what did I just get?" helper -- the thing you run before
    writing any real code against an unfamiliar endpoint.

    Picture the actual moment. An interviewer gives you a URL you have never
    seen. You do not know whether the body is one record or a thousand, what
    the fields are called, or whether it is JSON at all. Guessing costs you
    ten minutes; asking costs you one call. This function is the lesson's
    six-line exploration recipe packaged up so you can point it at anything
    and get a flat, printable answer back.

    It takes a Response object -- not a URL. It does no fetching of its own,
    so you can hand it any response you already have.

    Return a dict:
    {
      "status": <int>,
      "ok": <bool>,                 True when status < 400
      "content_type": <str>,        from the header; "" when absent
      "is_json": <bool>,            did the body actually parse as JSON?
      "shape": <str>,               "list" | "dict" | "other" | "invalid"
      "size": <int>,                len(data) for list/dict, else 0
      "keys": <list[str]>,          sorted top-level keys for a dict,
                                    sorted keys of the FIRST element for a
                                    list of dicts, else []
    }

    "invalid" shape means the body did not parse as JSON at all -- in which
    case is_json is False, size is 0 and keys is [].

    Do not assume the header exists, and do not assume the body is JSON just
    because the header claims it is. Both lie in the real world.

    That second warning is the whole point of the function, so it is worth
    spelling out. Content-Type is a header, and a header is just a line of
    text the server chose to send. A misconfigured server, a proxy in front of
    it, or an error handler that never got updated will cheerfully announce
    "Content-Type: application/json" and then send you an HTML error page.
    If you trusted the header you would report is_json as True and be wrong.

    So do not ask the header whether the body is JSON. Ask the body. Try to
    parse it, and record whether the parse actually succeeded -- that is what
    is_json means here. The header still goes in the output, because it is
    useful evidence when the two disagree, but it is evidence rather than
    truth. One of the tests is exactly this case: a 500 with an HTML body.

    The other thing to be careful about is the "keys" field, because a list
    and a dict need different treatment and a list might not contain dicts at
    all. For a dict, the keys are its own top-level keys. For a list, they are
    the keys of the first element -- but only if there is a first element and
    only if that element is itself a dict. A list of plain numbers has no
    keys, and reaching for them would crash. Sort them in both cases, so the
    same response always describes itself the same way.

    Use isinstance() to ask what you are holding rather than guessing, and
    remember that requests' JSONDecodeError is a kind of ValueError, so a
    single `except ValueError` covers the failed parse.
    """
    # TODO
    raise NotImplementedError


def get_user(username):
    """Fetch one GitHub user. Return the dict, or None when they don't exist.

    Ask GitHub for /users/<username>. If that user exists, return their record
    as a dictionary. If they do not, return None.

    A 404 means "no such user", which is a legitimate answer, not a crash.
    Any other error status should still raise.

    You cannot use fetch_json directly for this -- raise_for_status would
    turn the 404 into an exception. Make the request yourself and check the
    status before deciding.

    This is the most interesting judgment call in the unit, so sit with it for
    a moment rather than just copying the shape. fetch_json is a good function
    and you should reuse it almost everywhere -- but it calls
    raise_for_status(), and raise_for_status() treats every 4xx identically.
    Here, one of those 4xx codes does not mean anything went wrong. When you
    ask for a username nobody has taken and GitHub answers 404, the server is
    working perfectly and so are you. It is telling you a true fact about the
    world: that person is not there. That is data, and if you let it become an
    exception then checking whether a user exists -- an entirely ordinary
    thing to want to do -- crashes your program.

    So you make the request yourself, single out the 404, and translate it
    into None, which is unit 01's word for "there is nothing here". Every
    other bad status still goes through raise_for_status(), because a 500 or a
    403 genuinely is a problem and you want to hear about it immediately.

    This is unit 04's `d["key"]` versus `d.get("key")` decision one layer up:
    is absence a bug you want shouted at you, or is it a normal result you
    should carry forward? Being able to say which and why -- out loud, in an
    interview -- is worth more than the four lines it takes to write.

    Do send HEADERS and TIMEOUT. Skipping the plumbing because you are not
    using fetch_json is the mistake to avoid.
    """
    # TODO
    raise NotImplementedError


def get_repos(username, per_page=100, sort="updated"):
    """Fetch a user's repos (one page).

    Ask GitHub for /users/<username>/repos and hand back the list of
    repository dictionaries it returns.

    Uses fetch_json with the params per_page and sort.
    Returns the list of repo dicts.

    This one is short, and that is the point -- because fetch_json already did
    the headers, the timeout, the encoding and the status check, all this
    function has to decide is the URL and the two parameters. Both parameters
    are keyword arguments with defaults in the signature above, so a caller
    who does not care gets a sensible hundred-per-page sorted by most recently
    updated, and a caller who does care can override either.

    Note "one page". GitHub will not give you more than a hundred repositories
    in a single response no matter what you put in per_page; getting the rest
    means following pagination, which is unit 15. For now, one page is enough
    to work with and it is honest to say so in the docstring.
    """
    # TODO
    raise NotImplementedError


def summarize_user(user):
    """Reduce a raw GitHub user dict to the fields worth reporting.

    GitHub's user record has around thirty fields and you want six of them.
    Take the raw dictionary and build a small, flat, predictable one.

    Pure function -- no network. That is the point: it can be tested with a
    hardcoded dict, and it is where all your logic bugs would live.

    Take that seriously rather than reading past it. A "pure" function is one
    that only looks at its arguments and only produces a return value -- no
    fetching, no printing, no files. Because this one never touches the
    network, you can test it by typing a dictionary and calling it, and get an
    answer in under a second. Compare that to testing it through a live
    request: several seconds per run, one of your sixty hourly requests gone,
    and a failure that could be your logic or could be GitHub. Splitting the
    fetching from the transforming is unit 06's separation showing up for
    real, and the payoff is that the half where mistakes actually happen is
    the half you can iterate on instantly.

    {
      "login":      user["login"],
      "name":       user["name"] or "unknown",       # often null
      "public_repos": user["public_repos"] or 0,
      "followers":  user["followers"] or 0,
      "created_year": <int year from user["created_at"]>,   # None if absent
      "has_blog":   <bool>,          # truthy, non-empty "blog" field
    }

    created_at looks like "2011-01-25T18:44:36Z".
    Every field may be missing or null. None of it may crash.

    That last line is the actual exercise. One of the tests hands you an
    entirely empty dictionary and expects a complete summary back, and another
    hands you a record where half the values are explicitly null. Real GitHub
    users are like this: plenty have no display name, no blog, no company.
    So every single field here goes through unit 04's `.get()` rather than
    square brackets.

    And `.get()` alone is not quite enough, which is the trap in this
    function. `user.get("public_repos", 0)` still returns None when the key is
    present holding null, because a default only applies to a *missing* key.
    Since present-but-null is the common shape in real JSON, reach for
    `user.get("public_repos") or 0` instead -- unit 01's truthiness rules
    catching both cases at once. The same reasoning gives you "unknown" for a
    missing name.

    For created_year you want the four-digit year as an int. The timestamp is
    a fixed-width ISO string, so the first four characters are the year and
    slicing them off is entirely reasonable here -- but only once you know
    there is a string there to slice, since slicing None raises. For has_blog,
    note that both an absent blog and an empty-string blog should come out
    False, and that bool() of a falsy value is already exactly that.
    """
    # TODO
    raise NotImplementedError


def top_repos(repos, n=5):
    """Return the n most-starred repos as (name, stars) tuples.

    Given the list of repository dictionaries that get_repos handed you, rank
    them by star count and return just the best n, each as a two-item tuple of
    name and star count. If there are fewer than n repositories, return them
    all rather than complaining.

    Pure function. Sort by stars descending, breaking ties by name ascending.
    Missing stargazers_count counts as 0.

    top_repos(repos, 2) -> [("flask", 72117), ("click", 16800)]

    Pure again, and again that is deliberate -- one of the tests runs this
    against a saved file of real GitHub data with no network involved at all,
    which is exactly how you should develop against a live API: fetch once,
    save the JSON, then iterate on the transformation for free.

    This is unit 07's sorted-with-a-key applied to a real question. The tie
    rule is the part worth caring about: without one, two repositories with
    identical star counts can come back in either order, so your report
    changes between runs for no visible reason and stops being trustworthy.
    A key function that returns a tuple gives you the primary sort and the
    tiebreaker in one pass -- negate the star count so that larger sorts
    earlier, and leave the name alone so equal scores fall back to
    alphabetical.

    Watch the missing field. "stargazers_count" is absent from one of the test
    repositories, and a repository with no recorded stars must sort as zero
    rather than crashing the comparison. `or 0` handles it, and the name needs
    the same treatment before you sort on it, since None and a string cannot
    be compared.
    """
    # TODO
    raise NotImplementedError


def user_report(username):
    """Tie it together: fetch a user and their repos, return one report dict.

    This is the whole unit in one function. Given a username, find out whether
    they exist, fetch their repositories, summarize both, and return a single
    dictionary a caller can print or serialize without any further work. Two
    network calls, three pure transformations, and one decision about what to
    do when part of it fails.

    {
      "user":  <summarize_user output>,   or None if the user doesn't exist
      "repos": <top_repos output, top 5>, [] if the user doesn't exist
      "error": None,                      or an error string
    }

    Behaviour:
      - unknown user  -> {"user": None, "repos": [], "error": "user not found"}
      - network error -> user/repos as far as you got, error set to the
                         string from safe_fetch
      - success       -> error is None

    Hint: use get_user for the existence check, then safe_fetch for the repos
    so a failure there doesn't destroy the user information you already have.

    That hint is the design of the function, so here is the reasoning behind
    it. The two calls are not equally important. If the user does not exist,
    there is nothing to report and you should say so and stop -- that is the
    first branch. But if the user exists and then the repositories call times
    out, you are holding perfectly good user information, and throwing it away
    because the second half failed would be a poor trade. So the first call
    goes through get_user, which draws the exists/does-not-exist distinction,
    and the second goes through safe_fetch, which hands failure back as a
    value instead of an exception. You then put that value in the "error"
    field and return everything you did manage to get.

    This is why safe_fetch returns a pair rather than raising. A function that
    raised would have taken this decision out of your hands. One of the tests
    checks exactly this: repositories time out, the user survives, repos comes
    back empty, and error starts with "Timeout".

    Do the transforming with the pure functions you already wrote --
    summarize_user on the user dict, top_repos on the repository list, top 5.
    And remember that safe_fetch hands you None for the data when it failed,
    so give top_repos an empty list rather than None to work on.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    who = sys.argv[1] if len(sys.argv) > 1 else "pallets"
    print(json.dumps(user_report(who), indent=2))
