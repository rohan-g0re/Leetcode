"""Unit 18 task — API JSON into a clean DataFrame.

Eight functions. The first four are small, reusable cleaning helpers — the kind
of thing you write once and keep in your head for every dataset afterwards. The
last four use those helpers to turn three genuinely real API payloads into
tables you would be willing to compute an average from.

The three payloads were recorded from live services and edited in no way at
all, so each of them is awkward in its own particular fashion:

  hn_search_python      envelope + timestamps + a list column
  worldbank_population  [meta, records] + nested refs + nulls in the values
  placeholder_posts     clean, but needs joining to placeholder_users

Work through them in order. The helpers come first because the later functions
call them, and because writing a clean coercion helper once is exactly what
stops you from writing `errors="coerce"` slightly differently in six places.

Every function's docstring shows the exact columns, order, and dtypes expected.
Those are the specification — the tests check precisely them, so read them as a
contract rather than as description. Where the prose and a listed example seem
to disagree, the example wins.

Run:  python -m pytest test_task.py -v
      python task.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


def load_json(name):
    """Read fixtures/<name>.json. Provided for you."""
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def normalize_columns(df):
    """Return a COPY of df with tidied column names.

    Each name: lowercased, dots and spaces and hyphens replaced by "_",
    surrounding whitespace stripped.

    ["User Name", "owner.login", "a-b", " x "]  ->  ["user_name", "owner_login", "a_b", "x"]

    Dotted names from json_normalize block df.query() and attribute access,
    so this runs on every frame you build.

    Why bother: different services spell the same idea three different ways —
    `userName`, `user_name`, `User Name` — and `pd.json_normalize` adds dots of
    its own when it flattens nested records. If you let that reach the rest of
    your program, every later line has to remember which convention this
    particular API used. Normalizing at the boundary means nothing downstream
    ever has to care. It is the same move you made on dictionary keys in unit
    04, applied to columns.

    Two details the tests check. Work on a copy and rebuild `out.columns`, so
    the frame the caller handed you comes back untouched — silently renaming
    someone else's data is the kind of side effect that causes bugs three
    functions away. And note the order of operations on each name: strip the
    surrounding whitespace before you substitute, or `" x "` comes out as
    `"_x_"` rather than `"x"`.
    """
    # TODO
    raise NotImplementedError


def coerce_numeric(df, columns, integer=False):
    """Return a COPY with the named columns converted to numbers.

    - use errors="coerce" so unparseable values become NaN rather than raising
    - when integer=True, convert to the NULLABLE "Int64" dtype so missing
      values survive (plain int64 cannot hold NaN)
    - columns not present in the frame are skipped silently

    coerce_numeric(df, ["latitude", "longitude"])
    coerce_numeric(df, ["population"], integer=True)

    Why bother: JSON has no way to promise you a number, so numbers arrive as
    text constantly — the World Bank fixture you use below is a live example.
    Summing a text column concatenates the strings instead of adding them, with
    no error and a plausible-looking wrong answer at the end, which is why
    unit 17 told you to read `df.dtypes` before anything else. This function is
    the fix, in one place.

    `errors="coerce"` is the argument that matters. Without it, the first
    unparseable cell raises and takes the whole job with it; with it, that cell
    becomes NaN and every other row survives. The habit that must go with it is
    counting what you lost afterwards — `series.isna().sum()` — because
    coercion is silent by design and will happily discard half your rows without
    saying so. `quality_report` below is where you do that counting.

    The `integer=True` path exists because a plain int64 column has no room to
    store "missing" at all. One gap and pandas promotes the entire column to
    float, so your IDs print as `1.0` and stop matching anything. Capital-I
    "Int64" is the nullable version: it keeps whole numbers whole and tracks
    missing values alongside them.

    Skipping absent columns rather than raising is deliberate too. It lets you
    call this with the same column list against payloads that do not all carry
    the same fields, which is the normal situation.
    """
    # TODO
    raise NotImplementedError


def coerce_datetime(df, columns):
    """Return a COPY with the named columns parsed as UTC-aware datetimes.

    Use errors="coerce" and utc=True. Missing columns are skipped.

    Why bother: JSON has no date type either, so every timestamp you ever
    receive is a string. Until you convert it, none of the `.dt` tooling exists
    for that column — no year, no month, no day name, no sorting that means
    anything.

    `utc=True` is not cosmetic and it is the reason this helper exists rather
    than a bare `pd.to_datetime` call at each site. Real feeds mix offset
    formats: some rows end in `Z`, some in `+05:30`. Parsed without `utc=True`,
    pandas cannot find one datetime type that fits them all, gives up, and
    hands back a column of plain Python objects that merely looks converted —
    and then every `.dt` accessor raises. With it you get a single
    timezone-aware column, meaning every value carries its offset and can be
    compared to any other one unambiguously.

    `errors="coerce"` does here what it did above: an unparseable timestamp
    becomes `NaT`, the missing marker for datetime columns, instead of raising.
    `.isna()` finds `NaT` just as it finds NaN.
    """
    # TODO
    raise NotImplementedError


def quality_report(df, key=None):
    """Describe the health of a frame, as a plain dict.

    {
      "rows": int,
      "columns": int,
      "missing": {column: count},        # only columns with 1+ missing
      "duplicates": int,                 # duplicate rows on `key`, or 0 when
                                         # key is None or absent from the frame
      "empty": bool,                     # True when there are no rows
    }

    Every value must be a plain Python type -- the tests json.dumps the
    result. pandas returns numpy ints, which json.dumps refuses.

    This is the "before I build anything, is this data usable" check, in a
    form you can print, log, or return from an endpoint.

    Why bother: this is the five-check ritual from the lesson, boiled down to
    the three checks that can be answered mechanically — how much is missing,
    is the key repeating, is there anything here at all. Running it the moment
    a frame exists is how you find out that your coercion quietly emptied a
    column, or that pagination handed you the same page twice.

    On the `int(...)` and `bool(...)` casts, because they look like pointless
    ceremony and are not: pandas does its counting in numpy, so `len(df)` and
    `.sum()` give you back numpy scalars rather than Python ones. They print
    identically, compare equal to ordinary integers, and `json.dumps` flatly
    refuses to serialize them — `TypeError: Object of type int64 is not JSON
    serializable`. Since the whole point of this report is that you can log it
    or return it from an endpoint, casting at the boundary is what makes it
    actually usable. The tests call `json.dumps` on your result for exactly
    this reason.

    Filter `missing` down to columns whose count is above zero. A report listing
    forty columns with zero missing is a wall of noise; the ones with a problem
    are the ones you want your eye to land on.

    The `duplicates` rules are worth reading carefully. A duplicate here means
    two rows agreeing on `key`, not two identical rows — you almost never care
    about full-row equality, you care about the primary key repeating. And when
    `key` is None, or names a column this frame does not have, report 0 rather
    than raising, so the function is safe to call on any frame at all.
    """
    # TODO
    raise NotImplementedError


def hn_frame(payload):
    """Build a clean DataFrame from a Hacker News Algolia search response.

    Steps:
      1. take payload["hits"]  (assume the envelope; if "hits" is missing or
         empty, return an EMPTY DataFrame with the right columns)
      2. keep only these source fields:
         objectID, title, author, points, num_comments, url, created_at
      3. rename to: id, title, author, points, comments, url, created
      4. id must be a string; points and comments nullable Int64
      5. created must be a UTC-aware datetime
      6. add "domain": the lowercase host from url, or NA when url is null
      7. add "month": created formatted as "YYYY-MM" (a string; NA when the
         timestamp did not parse)
      8. drop rows with no id

    Final column order:
        id, title, author, points, comments, url, domain, created, month

    Hint: Series.str.extract with a regex is a neat way to pull the host out
    of a URL column in one vectorized step. A regex like
    r"^[a-z]+://([^/?#]+)" captures everything after the scheme and before
    the first /, ? or #.

    This is the whole pipeline in one function, against a real recorded search
    response. The rows live under an envelope key rather than at the top level,
    the timestamps are strings, the point counts go missing on some hits, and
    a story submitted as text rather than a link has a null url.

    On step 1 and the empty case, which is a design decision rather than
    defensive noise. Returning an empty frame *with the right columns* means
    every caller downstream can ask for `df["points"]` or `list(df.columns)`
    and get a sensible answer instead of a KeyError. The shape of what you hand
    back is the same whether the search matched fifty stories or none, so
    nobody has to write a special case. Define the column list once as a
    module-level constant and use it both here and at the end, so the two can
    never drift apart.

    On step 6, the domain. `Series.str.extract` runs a regular expression over
    a whole column at once and gives you back what the pattern's parentheses
    captured. Those parentheses are a capture group — the part of the match
    you actually want kept, as opposed to the part that merely has to be there.
    In `r"^[a-zA-Z]+://([^/?#]+)"` the scheme and the `://` must match but are
    thrown away; only the host inside the parentheses comes back. Pass
    `expand=False` so you get one Series rather than a one-column DataFrame.
    The behaviour that makes this the right tool: any row where the pattern
    does not match — a malformed url, and crucially a null url — comes out as
    NA automatically, with no error and no special case from you. Lowercase the
    result, since hosts are case-insensitive and `Example.com` and
    `example.com` must not count as two different domains.

    On step 7, `.dt.strftime("%Y-%m")` formats the whole column at once and
    propagates missing values properly, so a row whose timestamp came back
    `NaT` gets NA rather than the literal string "NaT".

    One robustness note the tests exercise: a payload may not carry all seven
    source fields. Make sure each one exists before you select on the list of
    them, or the selection raises a KeyError on a payload that was merely
    sparse rather than broken.
    """
    # TODO
    raise NotImplementedError


def population_frame(payload):
    """Build a clean DataFrame from a World Bank indicator response.

    The payload is [metadata, records]. Each record:

        {"indicator": {"id": "SP.POP.TOTL", "value": "Population, total"},
         "country": {"id": "ZH", "value": "Africa Eastern and Southern"},
         "countryiso3code": "AFE",
         "date": "2023",
         "value": 720859132,
         "unit": "", "obs_status": "", "decimal": 0}

    Produce columns, in this order:
        country_code, country_name, year, population

      country_code  <- countryiso3code, stripped, "" -> NA
      country_name  <- country.value, stripped
      year          <- date, as a nullable Int64
      population    <- value, as a nullable Int64  (it is null for some
                       country-year pairs and must survive as NA rather than
                       forcing the whole column to float)

    Drop rows with no country_code. Sort by country_code then year ascending,
    and reset the index.

    Use pd.json_normalize on the records so the nested country dict flattens,
    then your own normalize_columns / coerce_* helpers.

    This payload is awkward in three separate ways and each one is
    representative. The rows are wrapped in a two-element array whose first
    element is pagination metadata, so you have to reach into position 1 rather
    than treating the top level as your records. The country is a nested
    dictionary, so a plain `pd.DataFrame` would leave it sitting in a cell —
    `json_normalize` turns it into `country.value`, which `normalize_columns`
    then turns into `country_value`, which you rename to `country_name`. Doing
    all your renaming in a single `df.rename(columns={...})` call keeps that
    mapping readable as one table.

    The third awkwardness is that this API uses the empty string `""` where
    most services would send `null` — aggregate regions like "world" have no
    ISO country code and get `""` instead. An empty string is a perfectly
    truthy-looking value to pandas, so `.dropna()` will not touch it. Strip the
    two text columns and convert `""` to `pd.NA` *before* you drop on
    `country_code`, or every blank-coded row sails straight through your filter.

    On the nullable `Int64` for population, which is the point of the exercise:
    plain `int64` cannot hold a missing value at all, so a single null would
    silently promote the whole column to float and every population would print
    with a `.0` on the end. As it happens, in this particular fixture every null
    population sits on a row that also has a blank country code, so those rows
    get dropped anyway and you would not notice the difference — which is why
    the test proves the point with a small synthetic payload instead. The dtype
    still matters, because the next indicator you pull will not be so tidy.

    Year is `Int64` too, for the same reason and one more: it arrives as the
    string "2023", and sorting strings is not the same as sorting numbers the
    moment your range crosses a digit boundary.
    """
    # TODO
    raise NotImplementedError


def posts_with_users():
    """Join the posts and users fixtures into one frame.

    posts:  {"userId", "id", "title", "body"}
    users:  {"id", "name", "username", "email", "address": {...}, "company": {...}}

    Produce columns, in this order:
        post_id, user_id, user_name, user_city, company, title_length

      post_id       <- post id
      user_id       <- post userId
      user_name     <- user name
      user_city     <- user address.city
      company       <- user company.name
      title_length  <- number of characters in the post title

    Use a pandas merge (how="left" on the post side), not a Python loop.
    Sorted by post_id ascending, index reset.

    Why a merge rather than a loop: this is the same join you built by hand in
    unit 04 — index one side into a dictionary, then walk the other side once
    and look each match up. `df.merge` is that algorithm, written in C, in one
    line, and it is what an interviewer expects to see once a DataFrame is
    already in your hands. `how="left"` keeps every post whether or not its
    user was found, which is what you want: a post with no matching user is a
    fact worth seeing as a null, not a row that quietly disappears.

    The detail that trips people up: rename the post `id` to `post_id` before
    you merge. Both frames have a column called `id`, and pandas resolves that
    collision by appending suffixes, so you end up with `id_x` and `id_y` and
    have to work out which is which. Renaming first means the merged frame
    never has an ambiguous column at all.

    Two assertions are worth writing around any merge you do, and worth saying
    out loud in an interview even when you do not type them. First, that the
    join key is unique on the right-hand side — if a user id appeared twice in
    the users frame, a left join would duplicate every post belonging to that
    user and your row count would grow without any error. Second, that the row
    count is unchanged afterwards: 100 posts in, 100 posts out. That pair
    catches nearly every join that has gone silently wrong.

    The users frame needs flattening first, since `address` and `company` are
    nested dictionaries — `pd.json_normalize` plus your `normalize_columns`
    turns them into `address_city` and `company_name`. Narrow the users frame
    down to just the four columns you want before merging; there is no reason
    to drag ten unused columns of email addresses and geo coordinates through
    the join.

    For `title_length`, `.str.len()` counts characters over the whole column at
    once, which is the vectorized equivalent of calling `len()` on each title.
    """
    # TODO
    raise NotImplementedError


def top_domains(df, n=5):
    """Return the n most common non-null domains as a DataFrame.

    Columns: domain, stories, total_points
      - stories       row count for that domain
      - total_points  sum of points (missing counts as 0)
    Sorted by stories descending, then domain ascending. Index reset.

    Works on the output of hn_frame. An empty input gives an empty frame
    with those three columns -- do not let this raise.

    Why bother: "which sources come up most, and do they actually get
    traction?" is the kind of question you get asked thirty seconds after you
    have a clean table, and it is a `GROUP BY domain` with a count and a sum —
    familiar territory, different syntax. In pandas that is
    `groupby("domain").agg(...)`, where each keyword you pass names an output
    column and says which input column to aggregate and how.

    Drop the null domains before grouping rather than after. A null domain is
    not a source, it is a story submitted as plain text with no link, so it has
    no business appearing in a ranking of sources.

    On the tie rule: sorting by stories descending alone leaves domains with
    equal counts in whatever order they happened to land in, so the same
    correct answer would print differently between runs and nobody could
    diff two reports. Adding `domain` ascending as a second sort key makes the
    output reproducible. This is unit 03's `top_n` tiebreaker, unchanged.

    The empty guard has to come first, before you touch a single column.
    `groupby` on an empty frame gives you back something with neither the rows
    nor the columns you promised, and the caller then fails on
    `result["stories"]` with an error that points nowhere near the real cause.
    Check `df.empty` at the top and return `pd.DataFrame(columns=[...])` with
    the three column names, so the shape of your answer never depends on how
    much data there was. An API that matched nothing is a normal Tuesday.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    hn = hn_frame(load_json("hn_search_python"))
    print(json.dumps(quality_report(hn, key="id"), indent=2))
    print()
    print(hn.head().to_string(index=False))
    print()
    print(top_domains(hn).to_string(index=False))
    print()
    pop = population_frame(load_json("worldbank_population"))
    print(pop.head().to_string(index=False))
