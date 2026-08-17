"""Unit 07 task — comprehensions and sorting.

Ten functions, and between them they are the whole job you were hired to do
with a list of records: pick a column out of it, drop the rows you don't want,
total something up, list the distinct values, put it in order, group it,
summarise it, label it. You have written all eight of those in SQL. This unit
is where you write them in Python.

Reach for a comprehension here even in the places where an ordinary `for` loop
would work perfectly well. In unit 03 I told you the opposite, and for a good
reason — loops show you the mechanics. You have seen the mechanics now, so the
goal this time is fluency: getting to the point where the one-line form is what
your hands type without deliberating about it.

The REPOS list below is trimmed real data from
https://api.github.com/users/pallets/repos, and I have kept its rough edges
rather than tidying them. One repo has `language` set to None. One has no
`forks` key at all. Two are archived. Those are not traps I invented; they are
what an API response looks like, and roughly half of these functions exist to
make you handle them on purpose rather than by accident.

Every docstring shows worked examples in the form `call -> expected result`.
Those lines are the specification — the tests check exactly those cases, so
read them as the contract rather than as decoration. If the prose and an
example ever seem to disagree, the example wins.

Run:  python -m pytest test_task.py -v
"""

REPOS = [
    {"name": "flask", "language": "Python", "stars": 66000, "forks": 16000, "archived": False},
    {"name": "jinja", "language": "Python", "stars": 10000, "forks": 1600, "archived": False},
    {"name": "click", "language": "Python", "stars": 15000, "forks": 1400, "archived": False},
    {"name": "meta", "language": None, "stars": 100, "forks": 30, "archived": False},
    {"name": "flask-website", "language": "HTML", "stars": 200, "archived": True},
    {"name": "werkzeug", "language": "Python", "stars": 6500, "forks": 1700, "archived": False},
    {"name": "itsdangerous", "language": "Python", "stars": 2800, "forks": 220, "archived": True},
]


def names_of(records):
    """Return the "name" of every record, in order.

    Take a list of dictionaries and hand back a plain list holding just the
    value stored under "name" in each one, in the same order the records came
    in. Nothing is dropped and nothing is rearranged — the output is exactly as
    long as the input.

    names_of(REPOS)[:2] -> ["flask", "jinja"]

    Why bother: this is `SELECT name FROM records` and it is the smallest
    possible comprehension, so write it first and get the shape into your
    fingers. Read the line you write out loud as a sentence — "give me the name,
    for each record in records" — because every other comprehension in this file
    is that same sentence with more clauses bolted on.

    An empty input has to give you an empty list, and if you write this as a
    comprehension you get that for free: there is nothing to loop over, so
    nothing is produced. You will notice that free empty-case handling
    repeatedly in this unit.
    """
    # TODO
    raise NotImplementedError


def active_python_repos(records):
    """Return the names of non-archived repos whose language is exactly "Python".

    Two conditions have to hold for a repo to make it into the result: its
    language must be the string "Python", and it must not be archived. Repos
    that fail either test simply do not appear. The ones that survive keep the
    order they had in the input, and the output is shorter than the input.

    Records whose "language" key is missing, and records where it is present but
    holding None, are both excluded — neither of those is Python.

    -> ["flask", "jinja", "click", "werkzeug"]

    Why bother: this is a `WHERE` clause with two conditions, and it is the
    single most common thing you will do to an API response. What makes it worth
    writing carefully is the messy data. `REPOS` contains a repo whose language
    is None and one that is archived, and your line has to survive both without
    a special case or an error.

    The construction you want is a **filter**: an `if` written *after* the `for`
    clause, with no `else` attached to it. A filter decides which items get into
    the result at all, so rejected records are never produced and the list comes
    out shorter. That is the opposite of what `label_sizes` at the bottom of
    this file needs, so keep the distinction in view — same data, opposite tool.

    One small gift, and it is worth understanding rather than just using. If you
    reach for the value with `.get()` rather than square brackets, you get None
    back both when the key is absent and when it is present holding None. And
    comparing None to the string "Python" with `==` is a perfectly legal
    question with the boring answer False. So the messy records exclude
    themselves and you write no extra branch at all.
    """
    # TODO
    raise NotImplementedError


def stars_by_name(records):
    """Return a dict mapping name -> stars.

    Turn the list of records into a single dictionary whose keys are the repo
    names and whose values are the corresponding star counts. Every record
    contributes one entry, so a seven-record input gives you a seven-entry
    dictionary.

    stars_by_name(REPOS)["flask"] -> 66000

    Why bother: this is the lookup table from unit 04, and it is the reason
    dictionaries exist. Once you have built it, answering "how many stars does
    flask have?" is one instant lookup instead of a loop that scans every record
    looking for a match. If you then need the same answer for a thousand names,
    the difference between the two approaches stops being a matter of taste.
    It is also what a join looks like underneath: build a lookup table from one
    side, then walk the other side and look each row up.

    The tool is a **dictionary comprehension** — same idea as a list
    comprehension, but with curly braces and a `key: value` pair in the front
    slot instead of a single expression. The colon is what makes it a dictionary
    rather than a set, which is a distinction worth noticing now because
    `distinct_languages` below wants the version without one.

    One thing to be aware of even though this data does not trip it: if two
    records shared a name, the later one would silently overwrite the earlier,
    and your dictionary would come out shorter than your list. That is worth
    checking for on real data.
    """
    # TODO
    raise NotImplementedError


def distinct_languages(records):
    """Return the sorted distinct non-None languages.

    Collect the language of every record, throw away the duplicates and the
    missing ones, and hand back what is left as a list in alphabetical order.
    Five of the seven repos are Python, so "Python" appears once in the result,
    not five times.

    -> ["HTML", "Python"]

    Why bother: this is `SELECT DISTINCT language FROM records WHERE language IS
    NOT NULL ORDER BY language`, and it is what you run first when someone hands
    you an unfamiliar endpoint. Before you can say anything useful about the
    data you need to know what values a field actually takes, and this is the
    one-line way to find out.

    Two pieces fit together here. A **set comprehension** — curly braces with no
    colon in the front slot — collapses duplicates for you, because a set holds
    each distinct value exactly once. Then wrap the whole thing in `sorted()`,
    because a set has no order at all; without that wrapper the same correct
    answer could come back in a different arrangement on a different run, which
    no test can check against.

    The None repo needs excluding, and a filter does it. Notice you cannot
    simply sort a set containing both None and strings — that is the error
    `sort_with_missing_last` is built around — so dropping it is not tidiness,
    it is what stops the line from crashing.
    """
    # TODO
    raise NotImplementedError


def total_forks(records):
    """Return the sum of "forks" across all records, treating missing as 0.

    Add up the "forks" value of every record and return the single number. One
    repo in `REPOS` has no "forks" key at all, and it should contribute zero
    rather than stopping the calculation.

    Use a generator expression inside sum() -- do not build a list.

    -> 20950

    Why bother: `SELECT SUM(forks) FROM records`, and the thing being taught is
    the shape rather than the arithmetic. A **generator expression** is written
    exactly like a list comprehension but with parentheses instead of square
    brackets, and when it is the only argument to a function you may drop even
    those, so it reads as `sum(... for r in records)`. It produces its values one
    at a time on demand instead of building the whole list first.

    On seven repos that saves nothing measurable. On fifty thousand rows it is
    the difference between a program and a memory problem, because the list
    version builds every value in memory, adds them up, and then throws the list
    away. Getting into the habit now means you write the cheap version by
    default: if the result goes straight into `sum`, `any`, `all`, `max` or
    `min`, use a generator; if you need the list itself, use a list.

    The missing key is the part that actually bites. `sum` cannot add None to
    anything, so pull each value with a `.get()` that supplies a default of 0.
    An empty input has to total 0, which `sum` already does on its own.
    """
    # TODO
    raise NotImplementedError


def rank_by_stars(records, limit=None):
    """Return names sorted by stars descending, breaking ties by name ascending.

    Put the records in order from most stars to fewest, then return just their
    names. When two repos have the same number of stars, the alphabetically
    smaller name comes first. If `limit` is a number, return at most that many
    names; if it is None, return all of them.

    rank_by_stars(REPOS, 3) -> ["flask", "click", "jinja"]

    Ties matter: given [("b", 5), ("a", 5)] as records, "a" must come first.

    Why bother: "give me the top ten" is what people ask for the moment you have
    fetched anything, and this is `ORDER BY stars DESC, name ASC LIMIT n`. The
    ranking is the easy half. The tie rule is the half that matters, because
    without one two repos on equal stars can come out in either order and your
    report changes between runs for no visible reason.

    The tool is `sorted(records, key=...)`. Think of `key` as a translator:
    Python never really sorts your dictionaries, it hangs a tag on each one,
    sorts the tags, and brings the records along. Return a **tuple** from the key
    and you get multi-column ordering, because tuples compare left to right —
    the first element decides, and only on a tie does Python look at the second.
    That comma in the tuple is doing the same job as the comma in `ORDER BY`.

    The awkward part is that one column wants descending and the other
    ascending, and `reverse=True` would flip both. Negate the number instead:
    the biggest star count becomes the smallest tag, so ordinary ascending order
    on the tags is descending order on stars, while the name in the second slot
    still sorts normally.

    Finally, the `limit`. You need no branch for the None case if you don't want
    one — slicing a list with a bound of None gives you the whole list back,
    because to Python an omitted slice bound and a None bound are the same
    thing. Being explicit about it is also fine and arguably clearer.
    """
    # TODO
    raise NotImplementedError


def sort_with_missing_last(records, field):
    """Sort records ascending by `field`, putting missing/None values LAST.

    Sort the records into ascending order by whatever key name is passed in as
    `field`. Records that have no usable value for that field — either the key
    is absent entirely, or it is present holding None — all go at the very end,
    after every record that does have a value.

    Ties (including among the missing ones) keep original order -- Python's
    sort is stable, so you get this for free as long as your key doesn't
    accidentally distinguish them.

    records = [{"n": 3}, {"n": None}, {"n": 1}, {}]
    sort_with_missing_last(records, "n")
        -> [{"n": 1}, {"n": 3}, {"n": None}, {}]

    Returns a new list; the input is not modified.

    Hint: a key returning a tuple whose FIRST element is a bool. False sorts
    before True.

    Why bother: this is the function that survives real data, and it is the one
    worth being able to write from memory in an interview. Every sort you have
    written so far quietly assumed the sort field is filled in on every record.
    API responses are not like that, and the failure is not a wrong answer — it
    is a crash, on the day the data changes, in code that worked yesterday.

    Here is the mechanism, because you cannot fix this without it. `sorted`
    works by comparing values against each other in pairs, asking "is this one
    smaller than that one?" over and over. Python has no answer to "is None
    smaller than 3?" — there genuinely isn't one, it depends what you're doing —
    so rather than guess, it raises TypeError and stops. `sorted([1, None])`
    fails for exactly this reason. Nulls sorting last is not something Python
    can infer; it is a decision you have to state.

    You state it with the key function. Return a tuple whose first element is a
    boolean saying whether the value is missing. Booleans sort as if False were
    0 and True were 1, so False comes first — every record that has a value gets
    a tag beginning False and lands in the front block, every missing one gets
    True and lands at the back. Only inside the front block does the second
    element of the tuple matter. Think of that boolean as an extra sorting
    column with two values, used to carve the data into "present" and "missing"
    before anything else is considered.

    That leaves one thing to be careful about, and it is where most attempts at
    this break. The second element of your tuple still has to be something
    comparable even for the missing records, because two missing records tie on
    the first element and Python then compares their second elements against
    each other. If one of them is None and the other is a number, you are back
    to the same TypeError you were trying to avoid — and the test data contains
    both flavours of missing, `{"n": None}` and `{}`, precisely to catch this.
    Make sure both kinds of missing produce the *identical* tag. Once they do,
    they compare equal, and Python's stable sort leaves them in their original
    order, which is what the example shows.

    Last requirement: return a new list rather than rearranging the caller's.
    `sorted()` does that already; the `.sort()` method does not.
    """
    # TODO
    raise NotImplementedError


def group_names_by_language(records):
    """Return {language: [names...]} using None for records without a language.

    Build a dictionary whose keys are the languages and whose values are lists
    of the repo names written in that language. Records with no language are not
    dropped — they collect under the key None, which is a perfectly good
    dictionary key.

    Names within each group keep their original order.
    Languages in the result dict may be in any order.

    -> {"Python": ["flask","jinja","click","werkzeug","itsdangerous"],
        None: ["meta"],
        "HTML": ["flask-website"]}

    Why bother: this is `GROUP BY language`, and it is the move that turns a
    flat list into something you can say a sentence about. It is also the one
    function in this unit where a comprehension is the wrong tool, which is
    worth meeting deliberately. A comprehension produces one output item per
    input item; grouping has to *accumulate* several inputs into one growing
    list, and that is not a shape a comprehension can express. So this one is an
    ordinary `for` loop, and it should be.

    The idiom inside the loop is unit 04's: for each record, look up its
    language in the result dictionary, creating an empty list for it if this is
    the first time you have seen that language, then append the name to
    whichever list you got back. Doing that lookup-or-create in one step is what
    `setdefault` is for, and it is the reason you do not need to check whether
    the key already exists.
    """
    # TODO
    raise NotImplementedError


def stars_summary(records):
    """Return a dict with count, total, mean (2dp), max_name.

    Answer four questions about the star counts in one go and return them as a
    dictionary with the keys "count", "total", "mean" and "max_name". The count
    is how many records there are, the total is their stars added up, and the
    mean is the total divided by the count, rounded to two decimal places with
    `round(value, 2)`.

    max_name is the name of the record with the most stars; ties broken by
    name ascending.

    Return {"count": 0, "total": 0, "mean": None, "max_name": None} for an
    empty input -- and make sure max() does not raise on it.

    Why bother: this is the `SELECT COUNT(*), SUM(stars), AVG(stars) ...` row
    that ends every piece of analysis, and it is what you would actually say out
    loud about an endpoint after fetching from it.

    The interesting part is the empty input, which is why the docstring spells
    that case out. An empty list is not a strange edge case you have to invent —
    it is exactly what a search that matched nothing hands you, and it will
    happen the first time someone runs your code against a real query. Two
    separate things go wrong on it. `max()` on an empty collection raises
    ValueError rather than returning anything, so either guard the empty case
    before you get there or pass `max` a `default=`. And a mean is total divided
    by count, so on empty input you would be dividing by zero — which is why the
    specification asks for None there rather than a number. "There is no average
    of nothing" is the honest answer, and returning None says it.

    For `max_name`, note the tie rule pushes you toward the same key-tuple trick
    `rank_by_stars` used. Sorting the records the way that function does and
    taking the first one gives you a correct answer with no extra thinking.
    """
    # TODO
    raise NotImplementedError


def label_sizes(records, threshold=5000):
    """Return [(name, "big"|"small"), ...] using stars vs threshold.

    Give every repo a label. Return a list of two-item tuples, each pairing a
    repo's name with either the string "big" or the string "small". Nothing is
    dropped: the output has exactly as many items as the input, and a repo with
    no "stars" key is labelled as if it had zero.

    A repo is "big" when stars >= threshold. Missing stars count as 0.

    label_sizes(REPOS)[:2] -> [("flask", "big"), ("jinja", "big")]

    One comprehension with a ternary inside. No if-filter.

    Why bother: this is `CASE WHEN stars >= 5000 THEN 'big' ELSE 'small' END`,
    the bucketing step you do before counting how many fall in each bucket. But
    the real reason it is the last function in the file is the contrast with
    `active_python_repos`. Both are one comprehension over the same records with
    a condition in them, and they need opposite constructions.

    That one filtered: an `if` written *after* the `for`, no `else`, output
    shorter than the input, rejected records gone. This one chooses: an
    `if/else` written *before* the `for`, in the front slot where the value
    goes. That form is called a **ternary expression** — "ternary" meaning three
    parts, a value, a condition, another value — and you read it straight off
    the page as "big if the count is high enough, otherwise small". Every record
    produces something, so the output is always the same length as the input.

    The reliable way to tell them apart is the `else`. A ternary must have one,
    because it sits where a value is required and there is no such thing as
    producing nothing. A filter must not have one, because there is nowhere for
    a rejected record to go. When you cannot tell which kind of line you are
    looking at, look for the `else`.

    Note `threshold` has a default of 5000 but callers may pass their own, so
    compare against the parameter rather than hard-coding the number. The
    comparison is `>=`, not `>` — a repo sitting exactly on the threshold counts
    as big, and one of the tests checks precisely that.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    print(rank_by_stars(REPOS, 3))
    print(stars_summary(REPOS))
