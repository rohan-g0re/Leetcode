"""Unit 16 task — analysis with nothing but the standard library.

This is the unit where the plumbing turns into an answer. Units 11 to 15 were
about getting data out of a live API; unit 14 in particular left you holding a
list of flat dictionaries. Here you finally do something with it — count it,
summarise it, group it, join it, and print it in a shape a human can read.

You are working with two real datasets that already live on disk, so nothing
here touches the network:

  - fixtures/hn_search_python.json    50 Hacker News stories
  - fixtures/placeholder_posts.json   100 posts, joinable to 10 users

Nothing here needs pandas, and at this size nothing here *should* use pandas.
Fifty records is a scale where a `Counter` and a loop are faster to write,
easier to explain out loud, and produce output you can read without a viewer.
Pandas arrives in unit 17 and is the right tool once the data is large; knowing
which side of that line you are on is part of the skill being tested.

Every function below is pure — data goes in, data comes out, nothing is fetched
and nothing is mutated in place. That makes each one trivially testable, which
is why the tests are as short as they are.

Each docstring shows worked examples in the form `call -> expected result`.
Those lines are the specification: the tests check exactly those cases, so read
them as the contract rather than as illustration. Where the prose and an
example seem to disagree, the example wins.

Run:  python -m pytest test_task.py -v
      python task.py          <- prints a full report
"""

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


def load(name):
    """Read fixtures/<name>.json and return the parsed data. Provided for you.

    This is unit 09's file reading and JSON parsing in one line, and it is
    written for you so that the rest of the file can be about analysis rather
    than about loading. Call it as `load("hn_search_python")` and you get back
    ordinary dictionaries and lists.
    """
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def parse_timestamp(text):
    """Parse an API timestamp into a timezone-AWARE UTC datetime, or None.

    This is the customs desk from the lesson. Every timestamp entering your
    program passes through here and comes out stamped UTC, so that nothing
    downstream ever has to think about timezones again.

    Must handle all of these, which is what you actually get in the wild:
      "2024-01-05T10:30:00Z"           <- trailing Z
      "2024-01-05T10:30:00.000Z"       <- fractional seconds
      "2024-01-05T10:30:00+00:00"      <- explicit offset
      "2024-01-05"                     <- date only (midnight UTC)
      1700000000                       <- epoch seconds (int or float)

    Anything unparseable -> None. Never raise.

    The reason it never raises: this function gets called once per record, in a
    loop, over data you did not create. One malformed timestamp in record four
    hundred should cost you that one record, not the whole job. Returning None
    lets the caller skip it and carry on, which is what bucket_by_month below
    does.

    A naive result (no tzinfo) is a bug, not a detail. A **naive** datetime is
    one carrying no timezone information — it says "midnight on the 5th" and
    genuinely does not know midnight where. An **aware** one says "midnight on
    the 5th, UTC", which identifies a real moment. Python refuses to compare
    the two and raises TypeError when you try, and that TypeError will surface
    in the middle of a sort, long after the parsing went wrong. So a date-only
    string must come back as midnight UTC, aware, rather than as a bare naive
    midnight. The tests check .tzinfo is not None on every path, including that
    one.

    One ordering trap, and it is the same one from units 01, 08 and 13:
    `bool` must be rejected before the numeric branch. In Python, True and
    False are integers underneath — isinstance(True, int) is True — so a naive
    "is this a number? then treat it as epoch seconds" check happily converts
    True into 1970-01-01T00:00:01. Test for bool first and reject it, then test
    for int and float.
    """
    # TODO
    raise NotImplementedError


def count_by(records, field, missing="unknown"):
    """Count records per value of `field`, as a Counter.

    This is `SELECT field, COUNT(*) FROM records GROUP BY field` with the
    machinery visible. Walk the records, pull out one field from each, and
    tally how many times each distinct value appears. Return a Counter — an
    actual Counter, not a plain dict, because the caller will want
    `.most_common()` on it and the tests check the type.

    Values that are None or absent are counted under `missing`.

    count_by([{"a": "x"}, {"a": "x"}, {"b": 1}], "a")
        -> Counter({"x": 2, "unknown": 1})

    That third record has no "a" key at all, and it still gets counted — under
    "unknown". This is a deliberate choice and worth understanding rather than
    just implementing. If you silently dropped records with a missing field,
    your counts would no longer add up to the number of records you started
    with, and nobody reading the report would be able to tell. Bucketing the
    gaps into a visible category means the total is always honest and the size
    of the "unknown" bucket is itself a finding: a category holding forty
    percent of your data tells you the field is unreliable.

    Note that `.get()` collapses two different situations into one here — the
    key being absent, and the key being present holding None. Both mean "no
    data", so both land in `missing`, which is what the second test checks.
    """
    # TODO
    raise NotImplementedError


def numeric_summary(values):
    """Summary statistics for a list of numbers, ignoring None entries.

    Return:
    {
      "count": int,
      "min": float|None, "max": float|None,
      "mean": float|None,      # 2dp
      "median": float|None,    # 2dp
      "p90": float|None,       # 2dp, nearest-rank
      "skewed": bool,          # True when mean > median * 1.2
    }

    An empty (or all-None) input gives count 0, None for every statistic,
    and skewed False.

    Start by filtering the Nones out, then guard the empty case before you
    compute anything. That guard is not optional politeness: every function in
    the `statistics` module raises StatisticsError on an empty list rather than
    returning None, and an empty list is exactly what you get when a category
    turns out to have no usable data in it. This is unit 01's divide-by-zero
    guard in a new coat.

    Nearest-rank p90: sort, take index min(int(0.9 * n), n - 1).

    A **percentile** is a value's position in the sorted data — the 90th
    percentile is the value below which ninety percent of everything sits.
    **Nearest-rank** means you sort the values, walk ninety percent of the way
    along, and point at whoever is standing there: no interpolation, so the
    answer is always a number that genuinely occurred. The min(...) is a clamp
    that stops p=100 running one index past the end.

    "skewed" exists so you have a one-word answer to "what does this
    distribution look like" -- which is the follow-up question after every
    "compute the average".

    Here is why that flag earns its place. The mean is the centre of gravity of
    your numbers, so one enormous value drags it a long way. The median is the
    middle of the queue, and it does not budge. When the mean sits well above
    the median, a handful of very large values are pulling the average upward
    and the mean is not describing a typical record — the data is **right-
    skewed**, meaning its long thin tail stretches toward the large values.
    Essentially every real-world count behaves this way: stars, followers,
    revenue, page views. `mean > median * 1.2` is a cheap threshold rather than
    a statistical test, but it fires on the cases worth mentioning and stays
    quiet on ordinary noise, and it lets a generated report say the word
    "skewed" without a human having to squint at the numbers first.

    Make sure `skewed` is a real bool. The tests use `is False` and `is True`,
    which compare identity rather than value, so a truthy-but-not-True value
    will fail even though it "looks right".
    """
    # TODO
    raise NotImplementedError


def group_stats(records, group_field, value_field, missing="unknown"):
    """GROUP BY group_field, aggregating value_field.

    Return {group_value: numeric_summary(values in that group)}.

    This is the three-step shape from the lesson, and it is the single most
    reusable thing in this unit. Collect the values into buckets keyed by the
    group field; aggregate each bucket by handing it to numeric_summary;
    format the result as a dictionary. Whatever the question — points per
    author, revenue per region, latency per endpoint — it is this function with
    different field names. If an interviewer asks you something grouped and
    your mind goes blank, start typing `groups = defaultdict(list)` and the
    rest follows.

    - a record whose group_field is None/absent goes under `missing`
    - a record whose value_field is None/absent contributes NO value, but
      the group still exists (so it may have count 0)

    group_stats([{"g": "a", "v": 1}, {"g": "a", "v": 3}, {"g": "b"}], "g", "v")
        -> {"a": <summary of [1, 3]>, "b": <summary of []>}

    That second rule is the interesting one and it is deliberate. Group "b"
    exists in the output with a count of 0 and None for every statistic, even
    though not one of its records had a usable value. It would be easy — and
    tempting — to drop it, since a group with nothing in it looks like noise.
    Don't. **A category that exists but has no data is itself a finding.** If
    every record tagged "b" is missing its value field, that is a real fact
    about your data source and quite possibly the most useful thing in the
    whole report. Dropping the group hides it, and nobody reading the output
    can tell the difference between "b never appeared" and "b appeared and had
    nothing measurable in it".

    Getting this right needs a little care in phase one: create the bucket for
    every record's group, and only then decide whether that record contributes
    a value to it. If you only create the bucket when you have a value to put
    in it, empty groups vanish.

    One last thing on the way out: return a plain dict. If you built the
    buckets with a defaultdict, `dict(...)` it before returning, so callers do
    not inherit a container that invents keys when they merely look at it.
    """
    # TODO
    raise NotImplementedError


def top_n_by(records, field, n=5, label_field=None):
    """Return the top n records by numeric `field`, descending.

    "Give me the top ten" is what people actually ask for once you have some
    data in front of you — the biggest stories, the busiest authors, the worst
    error rates. It is also the natural follow-up to spotting skew in
    numeric_summary: once you know a few large values are dragging the mean,
    the obvious next question is which ones.

    When label_field is None, return the whole record dicts.
    When given, return (label, value) tuples instead.

    Two return shapes from one function, because both are genuinely useful at
    different moments. You want the whole record when you are going to keep
    working with it, and a compact (label, value) pair when you are about to
    print it — which is exactly what format_table below expects to be handed.

    Ties: break by the label ascending when label_field is given, otherwise
    keep the original order (Python's sort is stable, so descending on the
    value alone already does that).

    Tie rules matter more than they look. Without one, two records with the
    same value can come back in either order, so your report changes between
    runs for no visible reason and nobody trusts it. Sorting is **stable** in
    Python, meaning items that compare equal keep the order they arrived in —
    which is a good enough tie rule when you have no label to fall back on, and
    is why the no-label case needs no extra work. When you do have a label,
    unit 07's trick applies: a key function returning a tuple sorts by the
    first element and then the second, so negating the value gives you
    descending on value and ascending on label in a single pass.

    Records with a None/absent value are treated as 0.

    Treating a missing value as 0 rather than skipping the record is a choice
    the tests pin down: a record with no value still appears in the ranking,
    just at the bottom. That keeps the output length predictable, which matters
    when a caller has asked for five rows and needs five rows.
    """
    # TODO
    raise NotImplementedError


def bucket_by_month(records, date_field):
    """Count records per "YYYY-MM", using parse_timestamp.

    This is where "is this growing?" gets answered. Parse each record's
    timestamp, reduce it to a year-and-month label with strftime("%Y-%m"),
    and tally.

    Return a dict (not a Counter) sorted by month ascending. Records whose
    timestamp will not parse are skipped entirely.

    Sorting works with a plain `sorted` and no key function, which is a small
    piece of good fortune worth understanding rather than accepting. Those keys
    are strings, and sorted is comparing them character by character as text —
    but because "%Y-%m" is fixed width and runs largest unit to smallest, text
    order and chronological order are the same order. The year dominates, and
    within a year the zero-padded month sorts correctly too. That is precisely
    why ISO 8601 puts the year first, and it means you can order time without
    any datetime objects surviving into your output.

    Skipping unparseable records rather than crashing on them is the payoff for
    parse_timestamp returning None instead of raising. One bad timestamp costs
    you one record.

    bucket_by_month([{"d": "2024-01-05"}, {"d": "2024-01-31"}, {"d": "2024-03-01"}], "d")
        -> {"2024-01": 2, "2024-03": 1}

    Note there is no "2024-02" key: this counts what exists, it does not fill
    gaps. Filling gaps is a decision the caller should make consciously --
    and pandas' resample (unit 19) is what does it for you.

    That distinction is worth a sentence more, because it is a genuine
    analytical decision rather than an implementation shortcut. A missing bar
    and a zero bar mean different things. "February is absent from this data"
    and "February happened and nothing occurred in it" are different claims,
    and only the caller knows which one is true — a report covering a whole
    year should show February as zero, while a report on data that only starts
    in March should not invent a February at all. So this function reports what
    it saw and leaves the interpretation upstream. When you get to unit 19,
    pandas' resample is the tool that fills the gaps for you, and by then you
    will know what it is doing on your behalf and why you have to ask for it.
    """
    # TODO
    raise NotImplementedError


def join_records(left, right, left_key, right_key, fields, prefix=""):
    """Left-join `right` onto `left`, copying selected fields across.

    This is SQL's LEFT JOIN, written out. "Left" means every record from the
    left side survives whether or not it found a partner; the right side only
    contributes extra columns where a match exists. Posts with their authors,
    transactions with their customers, orders with their regions — the moment
    you have two sources, somebody asks you to combine them, and this is the
    shape of the answer.

    - build a lookup of right records keyed by right_key
    - for each left record, find the match on left_key
    - produce a NEW dict: the left record plus prefix+field for each name in
      `fields` that exists on the matched right record
    - unmatched left records are kept, with no extra fields added

    join_records(
        [{"userId": 1, "title": "t"}],
        [{"id": 1, "name": "Leanne", "email": "l@x.com"}],
        "userId", "id", ["name"], prefix="user_",
    ) -> [{"userId": 1, "title": "t", "user_name": "Leanne"}]

    The `prefix` exists to stop a collision. Both sides may well have a "name"
    field meaning entirely different things, and copying one over the other
    would destroy data silently. Prefixing the incoming columns with "user_"
    keeps both, and it makes the result readable — anyone looking at
    "user_name" knows immediately where it came from.

    Build the lookup ONCE, outside the loop. A nested scan is O(n*m) and it
    is the thing an interviewer will notice.

    That notation is worth defining if it is new: big-O describes how the work
    grows as the inputs grow, ignoring constants. O(n*m) means "for each of the
    n left records, scan all m right records" — a hundred posts against ten
    users is a thousand comparisons, which is nothing, but ten thousand against
    ten thousand is a hundred million, which is a coffee break. Building the
    lookup first makes it O(n+m): one pass to index, one pass to use it,
    because a dictionary lookup is instant no matter how large the dictionary
    gets. This is a **hash join**, and that is the real name for it — the same
    algorithm a database performs internally when it joins two tables. Saying
    "I'll hash-join on user id" out loud is a short, precise sentence that
    tells an interviewer you know what the database has been doing for you.

    Do not mutate the left records. Copy each one into a new dict and add the
    extra fields to the copy; one of the tests checks that the caller's input
    comes back untouched. A function that quietly edits what it was handed
    gives different answers the second time you call it.

    One thing to be aware of even though the tests do not force it: building
    the lookup with one entry per key assumes the right side's key is unique.
    If two right records share a key, the later one silently overwrites the
    earlier one and you lose a row with no warning at all. Comparing
    len(right) against len(lookup) is a one-line check for that, and it is the
    first thing to look at when a joined result has mysteriously fewer rows
    than you expected.
    """
    # TODO
    raise NotImplementedError


def analyze_hn(hits):
    """Full report over Hacker News hits. Ties everything above together.

    This one needs almost no new thinking. Every piece of it is a function you
    have already written; the job here is composition — deciding what a useful
    report actually contains and assembling it from parts.

    That is worth noticing, because it is the shape of the interview task this
    whole course is aimed at. You will not be asked to invent an algorithm. You
    will be handed an endpoint and asked to say something useful, and the
    answer will be four or five small, boring, already-written pieces stacked
    together: how many, what do the numbers look like, which are the biggest,
    who or what produced them, and how does it move over time.

    {
      "count": <int>,
      "points": <numeric_summary of the "points" field>,
      "comments": <numeric_summary of "num_comments">,
      "top_stories": <top 5 as (title, points) tuples>,
      "by_author": <the 5 most common authors as (author, count) tuples>,
      "by_month": <bucket_by_month on "created_at">,
      "distinct_authors": <int>,
    }

    A note on "by_author": you want the five most common authors as
    (author, count) pairs, which is precisely what Counter.most_common(5)
    already returns, so count_by feeds straight into it with nothing in
    between. And "distinct_authors" is a count of unique values — the natural
    tool for that is a set, since building one collapses duplicates for free.
    In SQL you would write COUNT(DISTINCT author); here it is len() of a set.
    """
    # TODO
    raise NotImplementedError


def format_table(rows, headers):
    """Render a list of tuples as an aligned plain-text table.

    format_table([("a", 1), ("bbb", 22)], ["name", "n"]) ->
        name   n
        a      1
        bbb   22

    (column widths: "name" is 4 wide, the number column is 2 wide; the header
    row obeys the same alignment rules as the data rows)

    Rules:
      - each column is as wide as its widest cell (header included)
      - the first column is LEFT aligned, all others RIGHT aligned
      - columns separated by two spaces
      - no trailing whitespace on any line
      - returns one string with lines joined by "\\n" (no trailing newline)
      - an empty rows list still renders the header row

    Presentation is not a nicety. A readable table is the difference between
    "here are the numbers" and "here is the answer".

    Take the alignment rule seriously, because it is not decoration and there
    is a reason behind it. Labels go left because text is easiest to scan when
    every entry starts at the same column. Numbers go right because that is
    what makes their digits line up by place value — units above units, tens
    above tens — and once they do, a longer number is visibly a bigger number.
    You can compare magnitudes at a glance without reading a single digit.
    Left-align a numeric column and 9 and 1000 begin in the same place, and the
    column tells you nothing until you actually read it.

    The shape of the solution is two passes, and that is true of every table
    renderer ever written: **measure, then render.** First walk everything —
    header row included — to find how wide each column needs to be. Only then
    lay out each line at those widths. You cannot do it in one pass, because
    you do not know how wide column one is until you have seen the last row.

    Two mechanical notes. Cells will not all be strings — points are ints —
    so convert each to str before you measure its length or the len() call
    fails. And the no-trailing-whitespace rule is what forces you to strip the
    end of each rendered line: the final column is padded to its width like any
    other, which leaves invisible spaces hanging off the right edge of every
    short row.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    hits = load("hn_search_python")["hits"]
    report = analyze_hn(hits)

    print(f"{report['count']} stories, {report['distinct_authors']} distinct authors\n")

    print("points:", report["points"])
    print("skewed:", report["points"]["skewed"], "\n")

    print(format_table(report["top_stories"], ["title", "points"]))
    print()
    print(format_table(report["by_author"], ["author", "stories"]))
