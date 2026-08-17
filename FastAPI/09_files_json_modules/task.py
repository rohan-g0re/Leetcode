"""Unit 09 task — files, JSON, and modules.

Nine functions, and they split into two halves. The first five are the
plumbing: getting data out of a file and into Python, and getting your results
back out of Python and onto disk in a form somebody else can open. The last
four are where this course stops using data I invented for you.

Those last four work on `../fixtures/github_repos_pallets.json`, which is a
genuine, unedited response from
https://api.github.com/users/pallets/repos?per_page=100 — seventeen repository
records, eighty-one distinct fields between them, nested objects, and nulls
sitting exactly where you would rather have data.

Before you write a line, open that file in your editor and read one record
properly. Thirty seconds of looking is worth more than any explanation I can
give you here, because this is precisely the kind of thing somebody drops in
your lap in an interview and asks you to say something useful about.

Every function's docstring shows worked examples or an exact output shape.
Those are the specification — the tests check them literally — so read them as
the contract rather than as decoration. If the prose and an example ever seem
to disagree, the example wins.

Run:  python -m pytest test_task.py -v
"""

import json
from pathlib import Path

# `__file__` is a variable Python fills in automatically with the path to this
# source file, so `Path(__file__).parent` is "the folder this code lives in".
# Anchoring to that instead of writing a relative path like "../fixtures" means
# the code finds its data no matter which folder your terminal happens to be
# sitting in when you start python.
HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"


def read_json(path):
    """Read a JSON file from disk and give back the Python object inside it.

    Open the file at `path`, parse the JSON text in it, and return whatever it
    describes — a list, a dictionary, whatever the file happens to hold. There
    is no special JSON type in Python: parsing hands you the ordinary lists and
    dictionaries you have used since unit 03.

    Two requirements. The caller may pass either a `Path` object or a plain
    string, and both have to work, so do not assume you were handed one or the
    other. And read with `encoding="utf-8"` — on Windows, leaving the encoding
    out means Python asks the operating system, which answers with a legacy
    codepage, and the first accented character or curly quote in the file
    either crashes you with `UnicodeDecodeError` or, worse, comes back quietly
    mangled.

    The judgement call here is what to do when the file is not there. Do
    nothing: let `FileNotFoundError` fly straight out of your function to the
    caller. A fixture or a data file that has gone missing is a genuine bug in
    your setup, and you want to hear about it loudly and immediately, at the
    exact line that tried to read it. Swallowing it and returning something
    bland would let the mistake travel — you would get an empty report ten
    functions later and have no idea why. Contrast this deliberately with
    `read_jsonl` below, which faces the same situation and correctly makes the
    opposite choice.

    Why bother: this and `write_json` are the save-and-reload pair, and they
    are what let you stop hammering an API while you work. You fetch once, save
    the response to a file, and from then on you develop against the file —
    which is fast, works offline, gives you the same bytes every run so your
    results are comparable, and does not burn through somebody's rate limit
    because you are on your fortieth attempt at the parsing logic.
    """
    # TODO
    raise NotImplementedError


def write_json(path, data):
    """Write `data` to `path` as pretty-printed JSON, and return that path.

    Turn the Python object `data` into JSON text and put it in the file at
    `path`, encoded as UTF-8. A handful of details make the difference between
    a file you can use and one you cannot.

    Indent it by two spaces rather than cramming everything onto one enormous
    line. The file is going to be read by a human — probably you, tomorrow,
    trying to work out what a field is called — and indentation is what makes
    the shape of the data visible at a glance.

    Non-ASCII characters must survive as themselves. Written naively, `Zürich`
    comes out in the file as `Z\\u00fcrich`: still valid JSON, still parses back
    correctly, and completely unreadable to the person opening it. There is one
    keyword argument that turns that escaping off, and the test checks for it
    by looking for the literal word `Zürich` in the file.

    Create the parent directory if it does not already exist. Writing to
    `output/reports/repos.json` when `output/reports` has never been created
    raises `FileNotFoundError`, which is a maddening error to get from a
    *write*. One `pathlib` call with two flags makes the whole chain of missing
    folders and does nothing if they are already there.

    Return the path you wrote to. Small courtesy, but it means the caller can
    write `print(f"saved to {write_json(p, data)}")` in one line.

    Why bother: this is the other half of the save-and-reload pair. `read_json`
    gets your saved copy back; this is what makes the saved copy in the first
    place, and it is also how you hand your results to somebody else.
    """
    # TODO
    raise NotImplementedError


def read_jsonl(path):
    """Read a JSON Lines file and return its records as a list.

    A JSON Lines file (`.jsonl`) is one complete JSON object per line — no
    wrapping array, no commas between records. So reading one means walking the
    file line by line and parsing each line on its own, collecting the results
    into a list. Skip any blank lines you meet rather than trying to parse
    them: a trailing newline at the end of a file is completely normal, and a
    blank line is not an error, it is just nothing.

    Now the interesting part, and it is the mirror image of `read_json`. If the
    file does not exist, return an empty list. Do not raise.

    That looks inconsistent until you ask what a missing file *means* in each
    case. For `read_json` the file is input — a fixture somebody promised you —
    so its absence is a bug and crashing is the helpful response. Here the file
    is an output log that your own program appends to as it goes, and the very
    first time you run anything it will not exist yet. Nothing has gone wrong;
    you simply have no records yet, and an empty list is the honest and correct
    description of that. Crashing on it would force every caller to wrap you in
    a try/except that always means the same thing.

    The general rule worth carrying away: a missing file is an error when
    somebody else was supposed to put it there, and normal when you are the one
    who fills it in.
    """
    # TODO
    raise NotImplementedError


def append_jsonl(path, record):
    """Add one record to the end of a JSON Lines file, without touching the rest.

    Serialize `record` to a single line of JSON, put a newline on the end of
    it, and add that line to the file at `path`. If the file does not exist
    yet, create it. Then return how many lines the file holds afterwards — so
    the first call on a new file returns 1, the second returns 2, and so on.
    You already have a function that reads the file back; there is no rule
    against calling your own work.

    The hard requirement is the one in the name: you must **not** read the
    existing file, add to it in memory, and write the whole thing back. Open in
    append mode and write only your one new line. Everything already on disk
    must be left exactly as it was, untouched, unread.

    Why bother, and why this format exists at all: imagine you are paginating
    through ten thousand records and the connection dies at nine thousand. If
    you were accumulating into a list in memory, you now have nothing — the
    process is gone and so is the list. If you were appending JSONL, you have
    nine thousand records sitting on disk, complete and parseable, and you can
    restart from where you stopped. A plain `.json` file cannot do this,
    because a JSON array has to be loaded, appended to, and rewritten whole
    every single time, which gets slower as it grows and leaves you with a
    truncated, unparseable file if you happen to die mid-write.

    Think of a JSONL file as a ledger: you only ever add a line to the bottom,
    and what is already written is never edited. That is what makes a long job
    survivable.
    """
    # TODO
    raise NotImplementedError


def write_csv(path, rows, fieldnames=None):
    """Write a list of dictionaries to a CSV file with a header row.

    `rows` is a list of flat dictionaries — the shape unit 04 told you to aim
    for and the shape `slim_repos` below produces. Write them to `path` as a
    CSV: one header line naming the columns, then one line per row. Return the
    number of data rows you wrote, not counting the header.

    `fieldnames` decides two things at once: which columns exist and what order
    they come in. When the caller passes it, use it as given. When it is `None`,
    take the keys of the *first* row, in the order they appear in that
    dictionary, and use those. Dictionaries have remembered their insertion
    order since Python 3.7, so "the order they appear" is a real, dependable
    thing and not luck.

    Four requirements, each of which exists because of a specific thing that
    goes wrong without it.

    First, a row may carry keys that are not in `fieldnames`, and those keys
    must be silently dropped rather than causing an error. The default
    behaviour raises `ValueError: dict contains fields not in fieldnames`,
    which would mean one stray field on record four hundred kills a report that
    was otherwise fine. There is a keyword argument that switches this to
    ignoring the extras; find it.

    Second, the reverse: a name in `fieldnames` that is missing from a
    particular row must come out as an empty cell, not an error. Real records
    do not all carry the same keys — that is the whole point of
    `repo_field_names` further down — and a CSV with a blank cell is a perfectly
    good answer.

    Third, the empty-`rows` case splits on whether you were told the columns.
    Given `fieldnames`, write the header and nothing else, because you know
    what the columns are even though no records matched, and a header-only CSV
    is a meaningful "the query returned nothing" that opens fine in Excel.
    Without `fieldnames` and without rows you genuinely do not know what the
    columns would have been, so write an empty file rather than inventing them.

    Fourth, and this one is Windows-specific and catches everybody: open the
    file with `newline=""`. The csv module writes its own line endings, and
    Python's text layer then translates them a second time, so without that
    argument you get a blank line between every single record. It looks like a
    bug in your code, it is not, and it will not reproduce on your colleague's
    Mac.

    Why bother: CSV is what you produce when a human is going to open the
    result, which is usually the real answer to "can you send me that?" It is
    also the format that makes your work visible to people who will never run
    your script.
    """
    # TODO
    raise NotImplementedError


def load_repos():
    """Load the GitHub fixture and return the list of repository records.

    Read `fixtures/github_repos_pallets.json` and hand back what is inside it,
    which is a list of seventeen dictionaries. This is one line: use the
    `read_json` you already wrote, and build the location from the `FIXTURES`
    constant at the top of this file and the filename.

    Notice what this function does *not* take: any arguments at all. It does
    not ask you where the file is, and it still works whether you run it from
    this folder, from the course root, from your editor's run button, or from
    pytest. That is entirely down to `FIXTURES` being derived from `HERE`,
    which is derived from `__file__` — the path is anchored to where this
    source file lives rather than to whatever folder your terminal was in. Had
    it been written as the obvious `read_json("../fixtures/...")`, it would
    work when you ran it by hand and throw `FileNotFoundError` the moment the
    test suite touched it, which is one of the most common ways a working
    script mysteriously stops working.

    Every other function below takes its repos as an argument. This one exists
    so that you, and the tests, have a single dependable way to get them.
    """
    # TODO
    raise NotImplementedError


def repo_field_names(repos):
    """Return every top-level field name that appears anywhere in the repos.

    Walk all the records, collect the keys of each one, and return the complete
    set of names as a sorted list. Sorted, and a list rather than a set,
    because the point of this function is that you are going to *read* the
    result — and a set prints in an unpredictable order, which makes it useless
    for eyeballing and impossible to test against. On this fixture the answer
    has eighty-one entries.

    The word "anywhere" is doing the work. You are not looking at the first
    record and calling it a day; you are taking the union across all of them,
    so a field that only two records carry still shows up. A set is the natural
    container for that, since it collapses the duplicates for free as you go —
    every record has a `name` key, and you want `name` once.

    Why bother: this is the second thing you run on an unfamiliar dataset,
    immediately after `len()` tells you how many records you are holding. It
    answers "what can I actually ask for?" and it is the only honest way to
    find out, because records in a real response genuinely do not all carry the
    same keys. That is unit 04's entire argument for `.get()` over `[]` — and
    this function is how you measure how bad the problem is *before* it bites
    you in the middle of a loop.

    If you ever want the stronger version of this in real work: instead of a
    set of names, build a dictionary counting how many records carry each key.
    A field present in 17 of 17 records is safe to index; one present in 3 of
    17 is a landmine.
    """
    # TODO
    raise NotImplementedError


def slim_repos(repos):
    """Reduce each repo to the six fields that matter, flattening as you go.

    This is the payoff function of the unit. Take the seventeen sprawling
    eighty-one-field records and return seventeen small flat dictionaries with
    exactly six keys each — no nesting, no surprises, nothing that can crash
    downstream. Flat means every value is a plain string, number, or None; you
    are pulling `owner` up out of the nested owner object rather than carrying
    the object along.

    Each output record:
        {
          "name":     repo["name"],
          "owner":    repo["owner"]["login"],       # nested
          "language": repo["language"],             # may be null
          "stars":    repo["stargazers_count"],
          "forks":    repo["forks_count"],
          "license":  license name, or None         # repo["license"] is often null
        }

    Five of those six are straightforward lookups. The licence is the one that
    will break your first attempt, so read this carefully.

    In this data, `repo["license"]` is one of two completely different things.
    On fourteen records it is a nested dictionary with a `"name"` key inside
    it, which is what you want. On the other three it is `null`, which arrives
    in Python as `None`. So the value you are after lives at
    `repo["license"]["name"]` on most records and simply does not exist on the
    rest — and the moment your loop reaches one of those three, that expression
    raises `TypeError: 'NoneType' object is not subscriptable`.

    The part that catches people is that the obvious defensive fix fails
    identically. `repo.get("license").get("name")` still explodes, because the
    first `.get()` succeeded — it found the key, and the key held `None` — and
    `None` has no `.get` method. Nor is `repo.get("license", {})` enough: a
    default value only fires when the key is **absent**, and here the key is
    very much present, sitting there holding `null`. You have defended against
    the wrong failure.

    The tool that does work is unit 04's `or {}` trick, which this unit's
    LESSON.md spells out in its last section. Read it as "the licence, or an empty dictionary if
    that turned out to be falsy, and then ask *that* for its name" — an empty
    dictionary answers `None` to any key you ask it, so the chain ends quietly
    instead of raising. It handles both the missing-key case and the
    present-but-null case in one expression, because `None` is falsy. The
    `language` field has the same null problem in a milder form: two records
    have `"language": null`, and here you simply keep the `None` as-is.

    Why bother: "slim it down to what I need" is the first transformation you
    perform on any real response, and unit 04 named this exact shape — a list
    of flat dictionaries — as the thing to always aim for. It is worth doing
    early and worth doing once, because everything downstream then gets to be
    simple. `language_report` below is just counting, and it is only just
    counting because this function already absorbed all the mess. The same is
    true of `write_csv`, which takes a list of flat dictionaries and nothing
    else.
    """
    # TODO
    raise NotImplementedError


def language_report(repos):
    """Summarize the repos by language and return the result as a dictionary.

    This is the "say something useful about it" step — the point of all the
    plumbing above. Produce one dictionary with exactly these four keys:

    {
      "total_repos":  <int>,
      "languages":    {<language or "unknown">: <count>, ...},
      "total_stars":  <int>,
      "top_repo":     <name of the repo with the most stars>,
    }

    Start by calling `slim_repos` on the input, and do the rest of your work
    against that result rather than against the raw records. You wrote it so
    that this function could be short; take the payment. Everything below then
    reduces to unit 05's counting-with-a-dictionary pattern.

    `languages` counts how many repos use each language. Repos whose language
    is `None` are counted under the string `"unknown"` — not dropped, and not
    left as `None`. Two reasons: the counts should still add up to the total
    number of repos, so "we could not determine this" stays visible instead of
    silently vanishing; and `None` cannot be a JSON object key, so a report
    with a `None` key in it would fail to serialize. The last test in the file
    checks exactly that by calling `json.dumps` on your report.

    `top_repo` is a ranking, so it needs a tie rule. When two repos have the
    same star count, the alphabetically first name wins. Without a stated rule
    two equally-starred repos can come out in either order, so your report
    changes between runs for no visible reason and nobody trusts it — the same
    argument unit 03's `top_n` made. Sorting by a tuple key gets you the
    primary sort and the tiebreaker in one pass.

    Why bother: this is what the person who handed you the URL actually wanted.
    Notice how little is happening here — a count, a sum, a max — and how that
    is only possible because `slim_repos` already handled every null. Getting
    the data clean early is what makes the interesting part easy.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    repos = load_repos()
    print(f"{len(repos)} repos")
    print(json.dumps(language_report(repos), indent=2))
