"""Unit 04 task — dicts and nested data.

This is the most useful task in Part 1. The nine functions below are, almost
word for word, the toolkit you will reach for the moment an interviewer hands
you a live API endpoint: reach into a nested response without crashing, pull
one field out of every record, group records the way SQL's GROUP BY would,
find out which columns are actually trustworthy, and summarise the result.
Write them once here and you will not have to think about them again under
pressure.

You do not need comprehensions for any of this — those are unit 07. Ordinary
`for` loops are fine, and while you are learning they are clearer to read and
easier to debug. If you already know comprehensions, use them.

Work through the functions in order; each one is a little larger than the one
before it, and the last one leans on ideas from the earlier ones. If you get
stuck on a function for around ten minutes, open `hints.md` — it explains the
approach without handing you the answer.

Run:  python -m pytest test_task.py -v
"""


def deep_get(data, *keys, default=None):
    """Walk down through a nested structure, one key at a time, without ever crashing.

    You hand it a dictionary and a series of keys, and it follows them inward:
    `deep_get(d, "a", "b", "c")` means "go into a, then into b, then get c."
    The whole point is what happens when that walk goes wrong. If a key isn't
    there, or a value along the way is None, or a value along the way turns out
    not to be a dictionary at all, you get `default` back instead of an
    exception.

    d = {"a": {"b": {"c": 1}}, "z": None}

    deep_get(d, "a", "b", "c")            -> 1
    deep_get(d, "a", "b")                 -> {"c": 1}
    deep_get(d, "a", "x", "c")            -> None
    deep_get(d, "z", "anything")          -> None
    deep_get(d, "a", "b", "c", "d")       -> None    (1 is not a dict)
    deep_get(d, "nope", default=0)        -> 0
    deep_get(d)                           -> the whole dict d

    Why bother writing this. Section 7 of the lesson showed you the single most
    common runtime error in API work: `repo["license"]["name"]` blowing up with
    "'NoneType' object is not subscriptable" because the licence field was
    genuinely null. Real responses are full of fields that exist on most
    records and are empty on some, and you find out which ones on record 400
    of 1000, after your job has already thrown its work away. This function is
    the permanent fix. Once it exists you can reach three levels into a
    response you've never seen before and know for certain that the worst case
    is a None, not a stack trace.

    Two pieces of syntax you haven't met. The `*` in `*keys` means "collect
    however many positional arguments the caller passed into a tuple named
    keys" — that's why the function works with one key, four keys, or none at
    all. And because `default` is written *after* `*keys`, Python makes it
    keyword-only: callers cannot pass it by position, they must spell out
    `default=0`. That's exactly what you want here, since otherwise a fourth
    key would silently be swallowed as the default.

    To get started, hold a variable — call it `current` — pointing at where
    you are in the structure, beginning at `data`. Loop through the keys,
    stepping `current` one level deeper each time. Before each step, ask
    yourself the two questions that make this safe: is `current` still a
    dictionary, and does it actually contain this key? If either answer is no,
    you are done and the answer is `default`. `isinstance` is the tool for the
    first question.
    """
    # TODO
    raise NotImplementedError


def pluck(records, key, default=None):
    """Pull one field out of every record and return the values as a list.

    Given a list of dictionaries and the name of a field, hand back a list of
    that field's value from each one. In SQL terms this is `SELECT one_column
    FROM records` — you are turning a table into a single column.

    pluck([{"a": 1}, {"a": 2}, {"b": 3}], "a")        -> [1, 2, None]
    pluck([{"a": 1}, {"b": 3}], "a", default=0)       -> [1, 0]
    pluck([], "a")                                     -> []

    Notice the third record in the first example has no "a" at all, and you
    still get an entry for it. That is deliberate and it is the important
    design decision here: the result always has exactly as many elements as
    there were records. If a caller wants the empties dropped, they can filter
    afterwards — but if *you* drop them, the caller's list of names no longer
    lines up with their list of scores, and nothing will tell them. Silently
    changing the length of a result is how two variables stop agreeing about
    which row is which, and it produces wrong answers that look completely
    plausible.

    This is the shape you use every time you want to feed one column into
    `sum`, `max`, or a chart. The tool you need is the `.get()` method from
    section 3 of the lesson, which already takes a default.
    """
    # TODO
    raise NotImplementedError


def index_by(records, key):
    """Turn a list of records into a dictionary you can look records up in.

    You have a list, and finding a particular record in it means scanning until
    you hit a match. Instead, build a dictionary once where each record's ID
    points at that whole record, and every lookup afterwards is instant.

    index_by([{"id": 1, "n": "a"}, {"id": 2, "n": "b"}], "id")
        -> {1: {"id": 1, "n": "a"}, 2: {"id": 2, "n": "b"}}

    Three details the tests check. A record that doesn't have the key at all is
    skipped entirely rather than being filed under None — there is no sensible
    ID to file it under. When two records share an ID, the one that appears
    later in the list wins, which falls out naturally if you just assign into
    the dictionary as you go. And you store the original record objects
    directly rather than making copies, so the dictionary and the list are
    pointing at the very same dictionaries in memory (unit 01, section 5).

    index_by([{"id": 1, "v": "old"}, {"id": 1, "v": "new"}], "id")
        -> {1: {"id": 1, "v": "new"}}

    Why this earns its place. This is a join. When an interviewer asks you to
    combine two sources — orders with their customers, posts with their authors
    — the answer is to index one side with this function and then walk the
    other side once, looking each match up. That is precisely what a database
    does internally for a hash join, and `index_by` is the build side of it.
    Doing it this way instead of a loop inside a loop is both dramatically
    faster on real data and much easier to explain out loud.
    """
    # TODO
    raise NotImplementedError


def group_by(records, key):
    """Sort records into buckets by the value of one of their fields.

    The result is a dictionary: each distinct value of the field becomes a key,
    and behind it sits the list of every record that had that value. This is
    SQL's `GROUP BY`, done by hand — except that instead of collapsing each
    group into an aggregate immediately, you keep the whole group, so you can
    decide afterwards what to compute from it.

    group_by([{"t": "x", "n": 1}, {"t": "y", "n": 2}, {"t": "x", "n": 3}], "t")
        -> {"x": [{"t":"x","n":1}, {"t":"x","n":3}],
            "y": [{"t":"y","n":2}]}

    Two rules. A record with no such field goes into the bucket under the key
    None — unlike `index_by`, you don't throw it away, because "how many
    records had no category?" is often the interesting answer. And within each
    bucket the records stay in the order they arrived, which matters when
    someone asks for "the first three of each type".

    Why this one matters more than the others. Almost every analysis question
    you will ever be handed is secretly this: sales per region, users per
    signup month, repositories per language. Get the records into groups and
    the rest is arithmetic. `summarize_records` at the bottom of this file is
    literally this function plus a mean.

    The tool that makes this three lines instead of ten is `setdefault`, from
    section 4 of the lesson. Look at what it returns when the key is already
    there versus when it isn't, and the shape of the loop should become
    obvious.
    """
    # TODO
    raise NotImplementedError


def select_fields(record, fields):
    """Keep only the fields you asked for, and build a new record from them.

    Given one record and a list of field names, return a fresh dictionary
    holding just those fields. Any name in your list that the record doesn't
    have is simply left out.

    select_fields({"a":1,"b":2,"c":3}, ["a","c","zz"])  -> {"a":1, "c":3}
    select_fields({}, ["a"])                            -> {}

    Two things the tests are strict about. Missing fields are omitted rather
    than filled in with None, because that preserves a distinction you'll want
    later: a field that's absent from the result was never sent by the API,
    while a field present in the result holding None was sent and was empty.
    Collapse those two together and you lose the ability to tell "the service
    doesn't have this column" from "this particular record had nothing in it".
    And you must not modify the record you were given — build a new dictionary
    and put things into it, rather than deleting keys out of the original.
    That input is very likely a record someone else is still holding a name
    for, and unit 01 section 5 explains why editing it in place would change
    it under their feet too.

    In practice this is how you cut a fat API response down to the handful of
    columns you actually intend to report on — a real GitHub repo record has
    around eighty fields and you probably want five.
    """
    # TODO
    raise NotImplementedError


def rename_keys(record, mapping):
    """Return a new record with some of its keys renamed.

    `mapping` is itself a dictionary, and it reads "old name -> new name". Walk
    the record, and for each key ask the mapping whether it has a replacement.
    Keys the mapping says nothing about keep the name they already had, and the
    values are never touched — only the labels change.

    rename_keys({"user_name": "x", "id": 1}, {"user_name": "name"})
        -> {"name": "x", "id": 1}

    Build the new record by walking the original in its own order, so the
    fields come out in the same sequence they went in (dictionaries have
    remembered insertion order since Python 3.7). As with `select_fields`, do
    not modify the record you were handed.

    Why you'll want this. Two services that hold the same information rarely
    agree on what to call it: one sends `user_name`, one sends `userName`, one
    sends `login`. If you rename at the boundary, the moment data arrives, then
    everything downstream — your grouping, your summing, your output — only
    ever has to know one set of names. Skip it and you end up with `if` checks
    for both spellings scattered through the whole program.

    The elegant version of the loop body is one line, and the trick is that
    `mapping` supports `.get()` with a default, exactly like any other
    dictionary. Ask yourself what default you'd want when a key has no
    replacement.
    """
    # TODO
    raise NotImplementedError


def count_missing(records, fields):
    """For each field you name, count how many records have no usable value in it.

    Go through every record and, for each field in your list, decide whether
    that record has real data there. A field is missing when the key is absent
    from the record, or when the key is present but holds None. Anything else
    counts as present — including an empty string and a zero, which are real
    values that a service genuinely sent you. That's unit 01's truthiness trap:
    if you test with `if record[field]:` then a legitimate `0` reads as missing
    and you will quietly overstate how bad your data is. Use `is None`.

    count_missing(
        [{"a": 1, "b": None}, {"a": None}, {"a": 3, "b": 2}],
        ["a", "b"],
    ) -> {"a": 1, "b": 2}

    Every field you asked about must appear in the result, even the ones where
    nothing was missing — a field with a count of 0 is the most useful entry in
    the report, because it's the column you can trust completely. So start by
    putting all the fields in at zero, then count upwards.

    Why this is the first function you should reach for. When a fresh dataset
    lands, you don't yet know which columns are populated. Running this tells
    you in one line that `name` is complete, `company` is 60% empty, and
    `location` is unusable — and that determines what analysis is even worth
    attempting. Doing it before you write anything else, and saying what you
    found, is exactly what an interviewer means by "tell me something about
    this data". Skip it and you'll build a chart on a column that turns out to
    be null for most rows.
    """
    # TODO
    raise NotImplementedError


def flatten_dict(data, prefix="", sep="."):
    """Squash a nested record down to one flat level, joining the key names with dots.

    A value buried at `data["b"]["d"]["e"]` comes out at the top level under
    the single key `"b.d.e"`. Nothing is lost; the path just moves from the
    structure into the name.

    flatten_dict({"a": 1, "b": {"c": 2, "d": {"e": 3}}})
        -> {"a": 1, "b.c": 2, "b.d.e": 3}

    flatten_dict({"a": {}})
        -> {}          <- an empty nested dict contributes nothing

    flatten_dict({"a": [1, 2], "b": None})
        -> {"a": [1, 2], "b": None}    <- lists and None are LEAF values

    Only dictionaries get opened up. A list is stored as it is, under its own
    key, and so is None — you stop descending the moment the value isn't a
    dictionary. `sep` lets the caller pick a different joining character, and
    `prefix` is the path accumulated so far, which is empty at the top.

    Why do this at all. A flat record is one row with columns, which is what
    a CSV file wants, what a spreadsheet wants, and what pandas wants. Unit 10
    says the target shape for any data task is a list of flat dictionaries, and
    when the API hands you three levels of nesting, this is the function that
    gets you there. In unit 18 you'll call `pandas.json_normalize` and it will
    do exactly this for you in one line — writing it by hand once means that
    when its output surprises you, you'll know precisely what it did.

    The technique here is **recursion**, which means a function that calls
    itself on a smaller piece of the same problem. It sounds stranger than it
    is. Walk the record's key/value pairs. When a value is an ordinary
    non-dictionary, you're at the bottom, so record it under prefix + key and
    move on. When a value *is* a dictionary, you have the same problem again on
    a smaller structure — so call `flatten_dict` on it, passing a longer prefix
    that includes the key you just walked through plus `sep`, and merge whatever
    comes back into your result. `dict.update` merges. Each call goes one level
    deeper, and the nesting is finite, so it always reaches the bottom and
    unwinds. Notice that the empty-dict case needs no special handling: an empty
    dictionary has no pairs to loop over, so it returns an empty result, and
    merging an empty result in adds nothing.
    """
    # TODO
    raise NotImplementedError


def summarize_records(records, numeric_field, category_field):
    """Summarise a numeric field for each category — the whole unit, in one function.

    Take the records, split them by the value of `category_field`, and for each
    of those groups work out how many usable numbers there were, what they add
    up to, and their mean rounded to two decimal places. The result is a
    dictionary from category value to a small dictionary with the keys
    "count", "total", and "mean". In SQL this is
    `SELECT category, COUNT(n), SUM(n), AVG(n) FROM records GROUP BY category`.

    records = [
        {"cat": "a", "n": 10},
        {"cat": "a", "n": 20},
        {"cat": "b", "n": 5},
        {"cat": "b"},              <- no "n": skipped from the maths
        {"n": 7},                  <- no "cat": category is None
    ]
    summarize_records(records, "n", "cat") ->
    {
      "a":  {"count": 2, "total": 30, "mean": 15.0},
      "b":  {"count": 1, "total": 5,  "mean": 5.0},
      None: {"count": 1, "total": 7,  "mean": 7.0},
    }

    Read that example carefully, because the awkward cases are the exercise.
    "count" is not how many records were in the group — it is how many of them
    had a usable number, so a record whose numeric field is absent or None is
    left out of all three figures. But the *category* still counts as having
    been seen: if every record in a group lacks the number, that group still
    appears in the output with count 0, total 0, and mean None. And a record
    with no category at all is filed under None, just as `group_by` does it.
    You can assume any numeric value that is present is already an int or a
    float, so no conversion is needed.

    The point of this function is the last line of unit 01 section 6: the mean
    is total divided by count, and count is zero exactly when a category turned
    out to have no usable numbers. Divide anyway and Python raises
    ZeroDivisionError and your whole run stops on one empty category. Guard it,
    return None for the mean, and the report still comes out — with an honest
    gap where the data was missing rather than no report at all. That guard is
    the most common defensive line in data work and this is where you practise
    writing it.

    The natural shape is two passes. First group the records by category —
    reuse the `group_by` you already wrote, which handles the missing-category
    bucket for you and guarantees every category that appeared gets an entry.
    Then walk each group, collect the values that are actually present and not
    None, and compute the three numbers from that list. `round(x, 2)` gives you
    the two decimal places.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    sample = {"a": {"b": {"c": 1}}, "z": None}
    print(deep_get(sample, "a", "b", "c"))
    print(deep_get(sample, "z", "nope", default="fallback"))
    print(flatten_dict({"a": 1, "b": {"c": 2}}))
