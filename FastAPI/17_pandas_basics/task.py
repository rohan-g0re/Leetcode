"""Unit 17 task — pandas basics.

Eight functions that take you all the way through a small pandas pipeline:
build a table from a JSON response, describe it, filter it, add computed
columns, group and aggregate it, and hand the result back out as plain
Python. That last step matters more than it sounds — it is how anything you
compute here reaches a FastAPI endpoint.

You work on two real fixtures rather than toy data. The GitHub repos file is
clean and well behaved. The World Bank countries file is not: it has
trailing spaces on values, empty strings where a null belongs, and numbers
that arrived as text. That contrast is deliberate, because the second one is
what real data actually looks like.

Nothing here touches the network and nothing prints — every function takes a
DataFrame (or nothing) and returns a DataFrame or a plain value. One rule
runs through all of them: do not modify the DataFrame you were handed.
Almost every pandas operation returns a new object rather than changing the
one you called it on, so you get this for free as long as you never assign
into the input. The one place you cannot get it for free is when you add a
column, and there you must `.copy()` first.

Every docstring below states its contract precisely — column names, their
order, how ties sort, what happens when something is missing. Those
statements are the specification; the tests check exactly them. Read them as
the contract rather than as description.

Run:  python -m pytest test_task.py -v
      python task.py
"""

import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


def load_json(name):
    """Read fixtures/<name>.json and return the parsed data. Provided for you.

    This one is already written. It opens the named file out of the shared
    fixtures folder, reads it as text, and hands the parsed result back — a
    list or a dictionary, depending on what that file contains. You call it
    at the top of `repos_frame` and `countries_frame`.
    """
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def repos_frame():
    """Build a DataFrame of GitHub repos from the fixture.

    Load `github_repos_pallets.json` and turn it into a table with these
    eight columns, in exactly this order:

        name, language, stars, forks, open_issues, archived, license, created

    Each one comes from a field of the raw repo record:

        name         <- name
        language     <- language              (may be null -> leave as NaN/None)
        stars        <- stargazers_count
        forks        <- forks_count
        open_issues  <- open_issues_count
        archived     <- archived              (bool)
        license      <- license.name          (license is often null)
        created      <- created_at            (leave as a string here; unit 19
                                               handles datetime conversion)

    Note that you are renaming as you go: GitHub calls it `stargazers_count`
    and your table calls it `stars`. That is normal and worth doing — the
    names in your table should suit the questions you are going to ask of it,
    not the internal vocabulary of whoever's API you happened to call.

    Two of these fields can be absent. `language` is null for repos GitHub
    could not classify, and `license` is null outright for a good number of
    them, which means the nested lookup `license.name` will blow up if you
    reach into it naively — this is unit 04's most common error, and
    `(repo.get("license") or {}).get("name")` is the fix.

    The method matters as much as the result. Build a plain Python list of
    flat dictionaries first, one dictionary per repo, and only then hand that
    list to `pd.DataFrame`. Do not try to make pandas understand the raw
    nested response. Going through the list of dicts is more reliable and far
    easier to read, because all the awkward null-handling stays in ordinary
    Python where `.get()` and `or {}` work and where you can print the
    intermediate result and look at it. It is also exactly the shape unit 14
    spent its length teaching you to produce — this line is what that was
    for.
    """
    # TODO
    raise NotImplementedError


def overview(df):
    """Return a small dict describing any DataFrame.

    Given any frame at all, hand back a summary of it in this exact shape:

    {
      "rows": int,
      "columns": list[str],           # in frame order
      "dtypes": dict[str, str],       # column -> str(dtype)
      "missing": dict[str, int],      # column -> count of NaN/None
    }

    Think of this as `df.info()` turned into data instead of printed text.
    `df.info()` prints a nicely formatted block to your terminal and returns
    nothing, which is fine when a human is looking at it and useless for
    anything else. You cannot write a test against it, you cannot store it,
    and you certainly cannot return it from an API. The same facts packaged
    as a dictionary can do all three — and later in this course this is
    literally what a `/data/summary` endpoint returns.

    One detail here is load-bearing rather than decorative. pandas hands back
    its own numeric types — a `numpy.int64` rather than a plain Python `int`
    — and `json.dumps` flatly refuses to serialize those. So the `int(...)`
    casts you will need around the counts are not tidying up; without them
    the function looks correct, the tests that inspect the values pass, and
    the one test that calls `json.dumps` on your result fails with a
    confusing message about a type not being serializable. Convert at the
    boundary, every time.

    It must work on an empty frame too, where the answer is zero rows and
    whatever columns that empty frame declares.
    """
    # TODO
    raise NotImplementedError


def filter_repos(df, min_stars=0, language=None, include_archived=False):
    """Filter the repos frame.

    Three conditions, two of which are optional:

    - keep rows with stars >= min_stars
    - when `language` is given, keep only that exact language
    - when include_archived is False, drop archived rows

    Return a new frame with a clean 0..n-1 index (reset_index(drop=True)).

    This is a `WHERE` clause assembled at runtime, which is a shape you will
    write over and over once you are building endpoints: the caller passes
    some query parameters, most of them optional, and you build the filter
    out of whichever ones actually arrived.

    The pandas way to do that is to build the mask up in stages. Start with
    the condition that always applies, then narrow it further with `&` for
    each optional condition that was supplied. Remember that a mask is just a
    column of True and False, so there is nothing stopping you from holding
    one in a variable and adding to it — and combining masks needs `&`, not
    the word `and`, because `and` wants a single true-or-false and you are
    handing it a whole column of them. Parenthesise every condition; `&`
    binds tighter than `>` and the error you get otherwise points nowhere
    useful.

    The `reset_index(drop=True)` at the end is not cosmetic. Filtering keeps
    the original row labels, so a frame filtered down to rows 4, 9 and 12
    still has 4, 9 and 12 as its index, and the caller who reasonably tries
    `result.loc[0]` gets a KeyError. Renumbering means the thing you return
    behaves like a fresh result set.

    Make sure it survives the boring cases: a `min_stars` so high that
    nothing matches should give you an empty frame, not an error. And the
    frame you were given must come back unchanged.
    """
    # TODO
    raise NotImplementedError


def add_metrics(df):
    """Return a COPY of the repos frame with three derived columns added.

        fork_ratio    forks / stars, rounded to 3dp; NaN when stars is 0
        popularity    "high" if stars >= 10000, "medium" if >= 1000, else "low"
        has_license   True when license is not null

    These are three computed columns, the same thing you would write as
    expressions in a SQL `SELECT` list. Compute each one over the whole
    column at once rather than looping over rows — `df["forks"] /
    df["stars"]` does every row in one instruction, and reaching for
    `.iterrows()` here is both slower and the thing a reviewer notices.

    Do not modify the input frame -- the tests check it is unchanged. That
    means the very first line of this function is `.copy()`. Adding a column
    is the one common pandas operation that changes the frame in place rather
    than returning a new one, so without the copy you would be quietly
    editing your caller's data. Copy first, then modify, always; it costs
    nothing and removes a whole category of bug.

    The zero-stars case is the interesting one and it is why this function
    exists. Dividing by zero in pandas does not raise an error the way plain
    Python does — it gives you `inf`. That is worse than an error, not
    better, because an exception stops you at the line that caused it whereas
    `inf` sails onward: it survives the rounding, it lands in your output
    column, and the moment anything downstream takes a mean of that column
    the answer for the whole group becomes `inf`. Now you have a wrong number
    in a report and no idea where it came from. Turn the zeros into NaN
    before dividing so the result is honestly missing.

    For `popularity`, note that the bands overlap in the way they are
    written: a repo with 50,000 stars satisfies both `>= 10000` and
    `>= 1000`, so whatever you write has to make the order of those checks
    unambiguous.
    """
    # TODO
    raise NotImplementedError


def language_summary(df):
    """One row per language, with aggregates. Returns a DataFrame.

    Columns: language, repos, total_stars, mean_stars, max_stars
      - repos       count of repos in that language
      - mean_stars  rounded to 1dp
    Rows with a null language are grouped under the string "unknown".
    Sorted by total_stars descending, then language ascending.
    Index reset to 0..n-1.

    This is a `GROUP BY` with four aggregates, and if you write the SQL out
    first the pandas falls into place:

        SELECT language, COUNT(name), SUM(stars), AVG(stars), MAX(stars)
        FROM repos GROUP BY language ORDER BY 3 DESC, 1 ASC

    The tool is `groupby` followed by a named aggregation, where each
    keyword argument you pass to `.agg` is one line of that SELECT list
    written backwards — the output name first, then a `(column, function)`
    pair saying what to aggregate and how.

    Two details are easy to miss. First, `groupby` puts the grouping column
    into the frame's index rather than leaving it as a column, so you need
    `reset_index()` to get `language` back out as an ordinary column where
    the tests expect to find it. Second, `groupby` ignores rows whose
    grouping key is null — so the two repos with no language would vanish
    entirely and your counts would not add up. Replace the nulls with the
    string "unknown" *before* grouping, on a copy, so those repos become
    their own visible category rather than silently disappearing.

    The two-level sort is `ORDER BY total_stars DESC, language ASC`, which
    `sort_values` does directly if you hand it a list of columns and a
    matching list of directions. The second key is a tiebreaker and it is
    there for the same reason it was in unit 03: without one, two languages
    with equal totals could come out in either order and your output would
    change between runs for no visible reason.

    Look up: df.groupby("x").agg(new_name=("col", "func")).reset_index()
    """
    # TODO
    raise NotImplementedError


def countries_frame():
    """Build a DataFrame from the World Bank countries fixture.

    This is the dirty one, and every step below is a real quirk of the World
    Bank response rather than an exercise invented to keep you busy.

    Start with the shape of the payload: it is a two-item list, `[metadata,
    records]`. The API puts paging information in the first slot and the
    actual data in the second, which means indexing straight into it and
    hoping is how you end up with a one-row frame full of page numbers. Take
    the second element.

    Those records are nested — `region` and `incomeLevel` are each a small
    dictionary rather than a value. `pd.json_normalize` flattens that for
    you, turning `{"region": {"value": "Europe"}}` into a column literally
    named `region.value`. It is the right tool here because the nesting is
    regular and shallow; it is not a substitute for thinking when the nesting
    is ragged.

    Then select and rename down to exactly these seven columns, in this
    order:

        code          <- id
        name          <- name
        region        <- region.value
        income_level  <- incomeLevel.value
        capital       <- capitalCity
        latitude      <- latitude
        longitude     <- longitude

    Then clean, in this order:
      - strip whitespace from every text column
      - replace empty strings with pd.NA  (the API uses "" for missing)
      - convert latitude and longitude to numeric with errors="coerce"
        (so unparseable values become NaN rather than raising)

    Each of those three is a real thing that happens. The trailing spaces are
    genuine: some region names arrive with whitespace on the end, and if you
    skip the strip you get "Europe & Central Asia" and "Europe & Central
    Asia " as two separate groups when you aggregate, with the counts split
    between them. The empty strings are the World Bank's idea of a null —
    aggregate rows like "Sub-Saharan Africa (excluding high income)" have no
    capital city, and the API sends `""` rather than `null`, which pandas has
    no reason to treat as missing. Converting those to `pd.NA` is what makes
    `.isna()` tell you the truth later. And the coordinates arrive as *text*,
    quoted in the JSON, which is precisely the dtype trap from the lesson: a
    latitude column of strings would let `.mean()` fail or misbehave rather
    than raise. `errors="coerce"` converts what it can and turns the blanks
    into NaN instead of dying on the first unparseable value.

    Column order must be exactly as listed above.

    Look up: pd.json_normalize(records, sep="."), df.rename(columns={...}),
    Series.str.strip(), Series.replace(), pd.to_numeric(..., errors="coerce").
    """
    # TODO
    raise NotImplementedError


def region_stats(df):
    """Per-region summary of the countries frame. Returns a DataFrame.

    Columns: region, countries, with_capital, mean_latitude
      - countries      number of rows in that region
      - with_capital   how many have a non-null capital
      - mean_latitude  mean of latitude ignoring NaN, rounded to 2dp
                       (NaN when the region has no latitudes at all)
    Rows with a null region are excluded entirely.
    Sorted by countries descending, then region ascending. Index reset.

    Another `GROUP BY`, but this one leans on how pandas' aggregation
    functions treat missing values, and it is worth being deliberate about
    rather than lucky.

    `"count"` ignores nulls. It counts the non-missing values in the column
    you point it at, not the number of rows in the group. That is exactly
    what `with_capital` wants — point `"count"` at the capital column and the
    rows with no capital simply do not count themselves. Meanwhile
    `countries` wants every row regardless, so point it at a column that is
    never missing, or count the group's size directly.

    `"mean"` skips NaN too, rather than being poisoned by it. So a region
    where four of five latitudes are present gives you the mean of those
    four, and you only get NaN back when *every* latitude in the group is
    missing — which is what happens to the "Aggregates" pseudo-region, since
    none of those rows are real places with coordinates. That NaN is the
    correct answer and the tests check for it.

    Regions themselves can be null, and unlike `language_summary` those rows
    are meant to disappear rather than become a category — so filter them out
    before you group, with `.notna()` rather than a comparison to None,
    because NaN is not equal to itself.

    Hint: a boolean Series sums as 1/0, so counting "how many are not null"
    is df["capital"].notna().sum().
    """
    # TODO
    raise NotImplementedError


def to_records(df, limit=None):
    """Convert a DataFrame to a list of plain dicts, JSON-safe.

    - when limit is given, take only the first `limit` rows
    - NaN / NA / NaT must become None, not float('nan')
      (json.dumps writes NaN, which is not valid JSON and breaks every
       downstream consumer -- including FastAPI)

    This is the exit door, and it closes the loop the module opened. You
    built the frame out of a list of flat dictionaries; `to_dict("records")`
    turns it straight back into one, a dictionary per row with the column
    names as keys. That symmetry is the whole architecture — plain Python at
    the edges where the data is messy, pandas in the middle where it is
    rectangular, and this function is the handoff back. FastAPI serializes
    lists of dictionaries perfectly happily and has never heard of a
    DataFrame, so in a few units' time this is literally the last line of
    your endpoint.

    The NaN conversion is the part that makes this more than a one-liner, and
    it is worth understanding rather than copying. `json.dumps` will cheerfully
    write the bare token `NaN` into its output — and `NaN` is not valid JSON.
    It is not in the specification. The reason this bug survives so long in
    the wild is that Python's own `json.loads` accepts it back out of
    politeness, so you can round-trip it through your own code and never
    notice a thing. Everything else rejects it: a JavaScript front end, a
    strict parser, FastAPI's own response validation. So convert missing
    values to `None`, which serializes to a proper `null`, before you hand
    anything over.

    One wrinkle when you do that: pandas will convert a `None` you put into a
    float column straight back into `NaN`, because that column can only hold
    floats. You have to loosen the column's dtype first so it is willing to
    hold an arbitrary Python object.

    to_records must produce something json.dumps accepts. The tests check
    exactly that.

    Look up: df.to_dict("records"), and how to replace missing values first.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    repos = repos_frame()
    print(json.dumps(overview(repos), indent=2))
    print()
    print(language_summary(repos).to_string(index=False))
    print()
    countries = countries_frame()
    print(region_stats(countries).to_string(index=False))
