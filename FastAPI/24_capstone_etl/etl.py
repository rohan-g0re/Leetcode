"""Capstone A — a Hacker News ETL tool.

    python etl.py "python" --pages 3 --min-points 50 --out reports/

ETL means extract, transform, load: fetch the data from wherever it lives,
reshape it into something usable, and write the result somewhere it survives.
This file is one such pipeline, split into fourteen functions across four
stages, and the stages are separated on purpose. Only the extract stage
touches the network. Everything after it is a pure function — data in, data
out, nothing else — which is why `test_etl.py` can check almost all of your
logic in a fraction of a second with the wifi switched off.

Nothing here is a new idea. The retry loop and the file cache are unit 15's,
the timestamp parsing and the statistics are unit 16's, the CSV and JSON
writing are unit 09's, and the habit of looking at one response before
writing anything is unit 14's. What is new is that you decide which piece
goes where. Go back and reuse what you already wrote rather than inventing
replacements — that reuse is the exercise.

Work top to bottom. Each stage feeds the next, so a function you skip is one
you will end up writing blind later.

Read README.md first, and poke at the live endpoint before you write anything.

The docstrings below are the specification. Where one names exact keys, an
exact column order or an exact substring, the tests check that literally, so
read those parts as a contract rather than as a suggestion. Where a docstring
says the layout is yours, it genuinely is.

Run the tests:
    python -m pytest test_etl.py -v -m "not live"
    python -m pytest test_etl.py -v
"""

import argparse
import hashlib
import json
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests

HERE = Path(__file__).parent
CACHE_DIR = HERE / ".cache"

HN_SEARCH = "https://hn.algolia.com/api/v1/search"
HEADERS = {"Accept": "application/json", "User-Agent": "python-api-course/1.0"}
TIMEOUT = 15


# ==========================================================================
# EXTRACT -- the only part that touches the network
# ==========================================================================


def make_session():
    """Return a requests.Session with HEADERS applied.

    A session is the object that carries your shared HTTP setup around and
    keeps the underlying connection open between requests, so fetching three
    pages does one handshake instead of three. Build it once here, hand it to
    everything else that needs the network, and the rest of this file never
    has to think about headers again.

    Apply the module-level HEADERS to the session itself rather than to each
    individual request — that is the whole point of having one. `Accept` tells
    the server you want JSON back, and `User-Agent` identifies your client,
    which some APIs insist on.

    Returning the session rather than stashing it in a global is what lets the
    tests hand your other functions a fake session that records calls instead
    of making them. Several tests in this file depend on that.
    """
    # TODO
    raise NotImplementedError


def cache_path(params, cache_dir=CACHE_DIR):
    """Deterministic cache file path for a params dict.

    Before you can save a response in a file you need a filename for it, and
    the request itself will not do — a params dict is full of characters a
    filesystem will not accept, and it has no natural length limit either. So
    you build a **cache key**: a short, fixed-length name that stands in for
    the request. The way to get one is to hash the request. A hash function
    takes any text and returns a fixed-length string of hex digits, such that
    the same input always gives the same output and two different inputs
    essentially never land on the same one. That buys you exactly what a
    filename needs to be — safe to write to disk, always the same length, and
    reliably different for different requests.

    Build the path as:

        <cache_dir>/hn_<first 16 hex chars of sha256 of the sorted json>.json

    Sixteen hex characters is sixty-four bits of name space, which is far more
    than enough that two of your cached requests colliding is not a thing that
    happens in practice.

    Serialise the params with json.dumps(params, sort_keys=True), and the
    `sort_keys=True` is the part that actually matters. json.dumps writes a
    dictionary's keys in whatever order they happen to sit in, so
    {"query": "x", "page": 1} and {"page": 1, "query": "x"} would serialise to
    two different strings and therefore hash to two different filenames — even
    though they are plainly the same request and should hit the same cached
    file. Sorting the keys first forces both to identical text. Leave it out
    and your cache still appears to work; it just silently misses whenever you
    happened to build the dict in a different order, which is a bug you would
    never think to go looking for. The tests check this case directly.
    """
    # TODO
    raise NotImplementedError


def fetch_page(session, params, cache_dir=CACHE_DIR, sleeper=time.sleep, attempts=3):
    """Fetch one page of search results, with cache and retries.

    This is the only function in the file that makes a network request, and it
    is two of unit 15's functions welded together: fetch_with_retry wrapped in
    cached_fetch. Go back and reuse what you wrote there rather than inventing
    something new — recognising that you have already solved this is the point
    of the exercise, and rewriting it from scratch is how you lose twenty
    minutes you do not have.

    The behaviour, in order:

    - if the cache file for these params already exists, return its parsed
      contents and make no request at all
    - otherwise GET HN_SEARCH with `params`, with retries:
        * retry on 429, any 5xx, requests.Timeout and requests.ConnectionError
        * wait sleeper(2 ** attempt) between tries
        * do NOT retry other 4xx -- raise via raise_for_status()
        * after the final attempt, re-raise
    - on success, write the parsed JSON to the cache file and return it

    The split between what you retry and what you do not is worth being able
    to justify out loud. A 429 means you went too fast and a 5xx means their
    server broke, and both of those can genuinely be different two seconds
    later. A 404 or a 401 cannot: the path is wrong or your credentials are
    wrong, and repeating the request just spends your rate limit three times
    over to learn the same thing. Backing off by 2 ** attempt gives 1 second,
    then 2, then 4, so each retry adds less load than the one before it rather
    than hammering a struggling server on a fixed beat.

    After the last attempt fails, re-raise rather than sleeping first. Waiting
    four seconds when you have already decided to give up is pure waste, and
    the tests inspect the recorded delays to make sure you do not.

    `sleeper` is a function passed in as an argument, defaulting to time.sleep
    and called as sleeper(seconds). It is a parameter because testing a retry
    loop against the real time.sleep would mean a test suite that genuinely
    sits there for seven seconds; the tests hand you a fake that appends the
    number to a list and returns instantly, so they can assert "it backed off
    1 second, then 2" in about a millisecond. In real use the default is what
    you want and you never pass this.

    The cache is the thing that makes the next hour bearable. You are going to
    run this script many times getting the logic right, and after the first
    run every one of those is instant and costs nothing from anyone's rate
    limit. The tests check that a second call with the same params does not
    touch the session at all — not that it is faster, that it makes no
    request.
    """
    # TODO
    raise NotImplementedError


def extract(session, query, pages=3, hits_per_page=100, tags="story", cache_dir=CACHE_DIR, sleeper=time.sleep):
    """Collect raw hits across pages, and report what you saw while doing it.

    This is the loop that calls fetch_page once per page and glues the results
    together. Two details of Hacker News search will catch you if you are
    working from habit. Its pages are numbered from ZERO rather than one, so
    the first request is page=0. And the response is an **envelope** — the
    stories are not the response itself but one field inside it, under
    "hits", sitting alongside metadata about the search:

        {"hits": [...], "nbHits": 3204, "page": 0, "nbPages": 33}

    So data["hits"] is your list of records and the rest is bookkeeping. Send
    query, tags, hitsPerPage and page on every request.

    Stop when:
      - "hits" comes back empty
      - you have fetched `pages` pages
      - you are on the last page (page >= nbPages - 1)

    Mind the off-by-one in that last one. With nbPages of 33 the pages run 0
    through 32, so the last page is nbPages - 1 rather than nbPages. Getting
    it wrong costs you one wasted request that comes back empty, which is not
    fatal but is exactly the kind of thing a reviewer notices.

    The `pages` cap is a different kind of stop condition from the other two.
    Those depend on you having read the server's response correctly; this one
    holds even when you have read it wrong. Without it, one misunderstanding
    on your side becomes thousands of real requests against somebody else's
    service.

    Return (hits, meta) where meta is:
        {"pages_fetched": int, "total_available": <nbHits from the first page>,
         "query": query}

    Returning the metadata alongside the data is a small thing that changes
    the report entirely. With it, you can say "287 of 3,204 matching stories,
    from the first 3 pages" instead of just "287". The first version tells the
    reader how much of the picture they are looking at; the second quietly
    invites them to assume they are looking at all of it. Being honest about
    the scope of what you pulled costs you one dictionary and buys you the
    difference between a number and an answer.
    """
    # TODO
    raise NotImplementedError


# ==========================================================================
# TRANSFORM -- pure, no network, fully testable
# ==========================================================================


def parse_timestamp(text):
    """ISO-8601 string (possibly with Z and fractional seconds) -> aware UTC datetime.

    This is unit 16's function; lift it from there. Hacker News sends its
    timestamps as text like "2024-05-06T12:00:00.000Z", and you need real
    datetime objects before you can sort by time, bucket into months, or work
    out a date range. The trailing "Z" means UTC, and the fractional seconds
    may or may not be there depending on the record.

    "Aware" means the datetime carries its timezone with it rather than being
    a bare wall-clock reading with no idea which clock it came from. Naive
    datetimes are the ones that produce off-by-a-few-hours bugs nobody can
    reproduce.

    Return None for anything unparseable rather than raising. Missing and
    malformed timestamps are normal in real data, and the caller — transform,
    just below — is going to count them rather than crash on them.
    """
    # TODO
    raise NotImplementedError


def domain_of(url):
    """Lowercase host from a url, or None.

    Pull just the host out of a URL and lowercase it, so that every story
    linking to the same site gets grouped together no matter how the URL was
    capitalised. This is the field the whole "top domains" section of the
    report is built on, and it is a derived field — it does not exist in the
    API response, you are creating it because it is the interesting
    categorical dimension hiding inside the url.

    domain_of("https://Example.COM/a?b=1") -> "example.com"
    domain_of(None) -> None
    domain_of("not a url") -> None

    Those last two cases are the reason this is a function rather than one
    inline expression. Plenty of Hacker News stories have no url at all — Ask
    HN posts, for instance — so None arrives regularly and must come straight
    back out. And urlparse does not raise on nonsense; it happily returns a
    result with an empty netloc, so a string that is not really a URL gives
    you "" rather than an error. Turn that empty string into None yourself, or
    you get a phantom domain of "" showing up in your top-domains table.

    urlparse is the tool, from urllib.parse, already imported at the top.
    """
    # TODO
    raise NotImplementedError


def transform(hits):
    """Raw hits -> (clean records, dropped count).

    This is the heart of the transform stage: take the messy, nested, partly
    null things the API gave you and produce a list of flat dictionaries with
    the same keys on every single one. That shape — a list of flat records —
    is what the CSV writer accepts, what every analysis function below expects,
    and what pandas would want if you reached for it. Getting to it is the
    first move of almost any data task.

    Each clean record:
        {"id": str, "title": str, "author": str|None, "points": int,
         "comments": int, "url": str|None, "domain": str|None,
         "created": <ISO 8601 UTC string>, "month": "YYYY-MM"}

    Two of those are derived rather than copied. `domain` comes from
    domain_of(url), and `month` is the "YYYY-MM" prefix of the parsed
    timestamp, which is what makes the per-month counts in analyze a one-liner
    later instead of a date-handling problem. Doing that bucketing once here,
    at the point where the record is built, rather than repeatedly downstream,
    is generally the right instinct.

    Note also that `created` goes back out as an ISO 8601 string rather than
    as the datetime object you parsed. That is deliberate: the report gets
    written to JSON at the end, and a datetime is not JSON-serializable.
    Parse it to validate and to derive the month, then store the text.

    Drop a hit when:
      - it has no objectID
      - its created_at will not parse

    Those two are the fields nothing downstream can work without — no id means
    you cannot identify the row, and no date means it cannot be sorted or
    bucketed. Everything else has a sensible fallback instead: missing points
    and comments become 0, and a missing title becomes "". Reach for .get()
    throughout, and remember that a key can be present holding null, so
    `hit.get("points") or 0` handles both absence and None where a bare
    default would only handle absence.

    Order is preserved. The API returned them in a meaningful order and you
    have no reason to scramble it.

    Return the records AND how many you dropped. Reporting the drop count is
    part of the job rather than an aside — a silent loss is exactly how a
    dataset quietly becomes wrong, because nobody ever goes looking for the
    records that were never there. "Fetched 300, kept 287, dropped 13 with an
    unparseable timestamp" is a sentence that takes you five seconds to say
    and tells an interviewer you have handled real data before.
    """
    # TODO
    raise NotImplementedError


def filter_records(records, min_points=0, domain=None, since=None):
    """Filter clean records down to the ones the caller asked for.

    Three independent filters, each switched off by default, and a record has
    to survive all of the ones that are switched on. This is the WHERE clause
    of the pipeline, and keeping it as its own function rather than folding it
    into transform matters: transform is about making records correct, this is
    about choosing which correct records you want, and the two change for
    different reasons.

    min_points  keep points >= this
    domain      exact match, case-insensitive; None means no filter
    since       "YYYY-MM-DD" string; keep records created on or after it;
                None means no filter

    The case-insensitive domain match is there because a user typing
    --domain A.COM on the command line means the same thing as a.com, and the
    stored domains are already lowercased by domain_of. Lowercase the incoming
    argument and compare.

    The `since` comparison is the detail worth slowing down for, because it
    looks like it should need date parsing and does not. Your `created` values
    are ISO 8601 strings, and ISO 8601 is designed so that alphabetical order
    and chronological order are the same order — biggest unit first, every
    field zero-padded to a fixed width. So "2024-03-01" > "2024-01-05" is True
    as plain text, for the same reason it is true as dates, and
    record["created"] >= since just works with no parsing at all. This is also
    why sorting records by their `created` string sorts them by time. It is
    the single most useful property of the format and it is not an accident.

    Order preserved.
    """
    # TODO
    raise NotImplementedError


# ==========================================================================
# ANALYZE -- pure
# ==========================================================================


def numeric_summary(values):
    """Describe one numeric column: count / min / max / mean / median / p90 / skewed.

    Unit 16's function again — lift it rather than rewriting it. Return a dict
    with those seven keys, rounding mean, median and p90 to two decimal
    places.

    The reason a summary has both a mean and a median is that comparing them
    tells you something. The mean is pulled around by extreme values and the
    median is not, so when the mean sits well above the median you are looking
    at a right-skewed distribution: a handful of very large values dragging
    the average up while most of the data sits lower down. That is exactly
    what Hacker News points look like — a few stories hit two thousand and the
    long tail is single digits — which is why "the average story has 47 points"
    is a misleading sentence and "the median story has 8 points, but the top
    one has 2,140" is an honest one. The `skewed` flag exists so the report
    can say that out loud without the reader having to compare two numbers
    themselves. p90, the value ninety percent of the data falls below, is the
    third view of the same shape.

    Empty input -> count 0 and None everywhere, skewed False. Guard for it
    explicitly: computing a mean is total / count, and count is zero the
    moment a filter turns out to exclude everything, which happens more often
    than you would like once --min-points is in play.
    """
    # TODO
    raise NotImplementedError


def analyze(records, meta=None, top_n=10):
    """Build the full report dict — the actual answer to "tell me something useful".

    Everything above this point was plumbing. This is the function that turns
    a pile of clean records into the thing a person reads, and it follows the
    order of `INTERVIEW_PLAYBOOK.md` §6: counts first, then the distribution
    of a numeric field, then group-and-aggregate, then time bucketing. Ship
    the boring one first and climb.

    Return exactly this shape:

    {
      "query": <from meta, or None>,
      "pages_fetched": <from meta, or 0>,
      "total_available": <from meta, or 0>,
      "records": <len(records)>,
      "points": <numeric_summary of points>,
      "comments": <numeric_summary of comments>,
      "date_range": {"first": <earliest created>, "last": <latest>},   # None,None when empty
      "top_stories": [ {"title":..., "points":..., "domain":...}, ... ],  # top_n by points
      "top_domains": [ {"domain":..., "stories":..., "total_points":...}, ... ],  # top_n
      "top_authors": [ {"author":..., "stories":...}, ... ],              # top_n
      "by_month": { "YYYY-MM": count, ... },                              # ascending
      "self_posts": <how many records have no domain>,
    }

    top_domains sorted by stories desc then domain asc; top_authors likewise.
    That secondary sort on the name is not decoration — when six domains all
    have four stories, sorting only by count leaves their relative order up to
    whatever your Counter happened to do, so the report comes out different on
    different runs and becomes impossible to eyeball or to test. A tie-breaker
    makes the output deterministic.

    Records with a null author or domain are excluded from those two lists.
    A "top domains" table with an empty row at the top is not information.

    Three of these fields deserve a sentence about what they actually tell a
    reader, because they are the ones that turn numbers into observations.

    `date_range` says how far back your data reaches. Without it nobody can
    tell whether "287 stories" covers a fortnight or a decade, and those are
    completely different claims. Both entries are None when there are no
    records at all.

    `self_posts` counts the records with no domain — stories with no outbound
    link, which on Hacker News means Ask HN and Show HN posts and other
    text-only submissions. It is worth its own number because a topic where
    half the stories are self-posts is a topic being discussed, whereas one
    where nearly all of them link out is a topic being reported on. That is a
    genuine observation about the data, drawn from a field that only exists
    because you derived it.

    `by_month` is the time series: how many stories per calendar month,
    ordered ascending so the reader can see a trend rather than hunt for one.
    Ordering matters here because dictionaries keep their insertion order, so
    building it in sorted order is the whole of the work.

    Everything must be JSON-serializable, because save_json writes this
    straight to a file. That means plain dicts, lists, strings, numbers, bools
    and None — no datetime objects, and no Counter objects left un-converted.
    The tests call json.dumps on your report to check exactly this.

    `meta` is optional, and when it is absent the query becomes None and both
    counts become 0. That lets analyze be called on records that did not come
    from extract at all, which is how most of the tests use it.
    """
    # TODO
    raise NotImplementedError


# ==========================================================================
# LOAD
# ==========================================================================


def save_csv(records, path):
    """Write records to CSV with a header row. Return the number of data rows.

    This is the "save the dataset so we can look at it later" half of the
    brief, and it is unit 09's file writing. The CSV is the artefact that
    outlives the run — somebody opens it in a spreadsheet tomorrow, and it has
    to make sense without you standing next to it.

    Columns, in order: id, title, author, points, comments, domain, url,
                       created, month

    That order is contract and the tests check the header line literally. It
    is also a reasonable order on its own terms: identifier first, then the
    human-readable fields, then the numbers, then the derived and technical
    ones. Note it is not the same order as the record dict, so pass the column
    list explicitly rather than trusting whatever order the keys came in.

    Create the parent directory if it is missing — the --out option can name a
    folder that does not exist yet, and failing on that would be a poor way to
    end a successful run. Write UTF-8, because story titles contain every
    character on earth.

    One Windows-specific trap worth knowing before it bites you. Python's csv
    module writes its own line endings, and if you open the file in the normal
    text mode Windows then translates those endings again, so you get a blank
    line between every row. The fix is to open the file with newline=""
    and let csv handle it. This is the single most common "why does my CSV
    look like that" question, and the answer is always this line.

    Return the row count, not counting the header. Callers want to know how
    many records landed on disk.
    """
    # TODO
    raise NotImplementedError


def save_json(report, path):
    """Write the report as pretty JSON (indent 2, non-ASCII preserved).

    The CSV holds the rows; this holds the conclusions. Two files rather than
    one because they answer different questions and get read by different
    things — a person opens the CSV in a spreadsheet, a program reads the
    JSON.

    `indent=2` costs a few bytes and makes the file readable by a human who
    opens it in an editor, which at this size is worth far more than the
    bytes. `ensure_ascii=False` is the non-ASCII part: by default json.dumps
    escapes every accented or non-Latin character into a \\uXXXX sequence, so
    a title in Japanese comes out as unreadable gibberish that is technically
    correct. Turning it off writes the real characters, and since you are
    already writing UTF-8 there is no downside.

    Create the parent directory here too, for the same reason as save_csv.

    Return the path, so the caller can print where the file went without
    reconstructing it.
    """
    # TODO
    raise NotImplementedError


def format_report(report):
    """Render the report as readable plain text. Return one string.

    This is the only part of your work the interviewer actually looks at, and
    it is worth more of your attention than its size suggests. The report dict
    already contains the answer; this function decides whether the answer can
    be read.

    Required content -- the tests check for these substrings, so treat this
    part as contract:
      - the query
      - the line "stories: <n>"
      - the word "points"
      - the word "domains"
      - each of the top 3 domain names

    Beyond those, the layout is genuinely yours, and that is deliberate. Build
    it as a list of lines and join them with newlines at the end rather than
    concatenating a string in a loop; it is easier to reorder and easier to
    read.

    Aim for something you would be happy to have on screen while somebody else
    reads it. Align your columns with f-string width codes so numbers line up
    on the right — f"{value:>8}" pads to eight characters, and a column of
    right-aligned numbers can be compared at a glance while a ragged one
    cannot. Use the thousands separator, f"{3204:,}" giving "3,204", because
    at four digits and up the commas are the difference between reading a
    number and counting its digits. Never print a raw dict; a line of Python
    repr on screen says you ran out of time.

    And say the things the numbers imply rather than making the reader derive
    them. "3 pages, 287 of 3,204 matching stories, 13 dropped" and "mean 47 vs
    median 8 — right-skewed, a few big stories are pulling the average" are
    both one line of formatting work, and both are the difference between
    handing someone the numbers and handing them the answer. That distinction
    is what this whole capstone is about.
    """
    # TODO
    raise NotImplementedError


# ==========================================================================
# CLI
# ==========================================================================


def build_parser():
    """Build the argparse parser for the command line.

    A CLI — command-line interface — is what turns your script into a tool
    somebody else can use: options typed after the program name instead of
    values edited into the source. **argparse** is the standard library module
    that handles this. You declare the options you accept, and it parses
    sys.argv for you, converts the types, applies the defaults, rejects
    nonsense with a sensible message, and generates the --help text for free.

    positional:  query
    --pages       int, default 3
    --min-points  int, default 0
    --domain      str, default None
    --since       str, default None      (YYYY-MM-DD)
    --out         str, default "reports" (a directory)
    --no-cache    flag, default False

    Two details of argparse's naming worth knowing before they confuse you.
    An option written --min-points on the command line arrives as
    args.min_points in Python, because argparse turns the hyphen into an
    underscore. And --no-cache is a flag rather than a value: it takes no
    argument, and you declare it with action="store_true" so that its mere
    presence sets it True and its absence leaves it False.

    Passing type=int on --pages matters more than it looks. Everything from
    the command line arrives as text, so without it --pages 3 gives you the
    string "3", and range("3") is an error some distance from its cause.

    Return the ArgumentParser itself rather than the parsed arguments. That
    separation lets the tests call .parse_args([...]) on it with a list they
    control, instead of your parser reading the real command line during a
    test run — the same dependency-injection idea as the `sleeper` argument
    further up.
    """
    # TODO
    raise NotImplementedError


def run(argv=None):
    """Wire the whole pipeline together. Return the report dict.

    Every other function in this file does one thing and knows nothing about
    the others. This is the one place that knows the order, and it should read
    like a table of contents for the program:

    1. parse args
    2. build a session
    3. extract (skip the cache entirely when --no-cache)
    4. transform, then filter
    5. analyze
    6. save <out>/stories.csv and <out>/summary.json
    7. print format_report(report)

    Keep it that thin. If you find real logic creeping in here, it belongs in
    one of the functions above, where it can be tested on its own.

    `argv` defaults to None, which is what argparse takes as "read the real
    command line". Passing a list instead is how the tests drive the whole
    program end to end without touching sys.argv.

    Somewhere between steps 4 and 7, remember the dropped count that transform
    handed you. It is the one number in the pipeline that will vanish if you
    do not deliberately carry it forward, and it is the one an interviewer
    most notices you mentioning.

    Return the report dict rather than only printing it. A function that
    prints and returns nothing can only be checked by capturing stdout and
    parsing the text back out, which is brittle and miserable; a function that
    returns its result can be inspected directly — report["records"] == 1 and
    you are done. That is exactly what test_run_end_to_end does. Printing is
    for the human, returning is for every other caller, and doing both costs
    you one line.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    run()
