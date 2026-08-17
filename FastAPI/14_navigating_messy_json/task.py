"""Unit 14 task — navigating messy JSON.

The first five functions are not exercises you do once and throw away. They
are a REUSABLE EXPLORER TOOLKIT: write them properly here, keep them, and you
can point them at any endpoint you have never seen before and know within a
minute what you are holding. That is worth taking seriously, so give these
five more care than their size suggests. The version of you sitting in an
interview with a strange URL on screen will be glad you did.

The last four functions apply that toolkit to three genuinely awkward real
responses, recorded exactly as the services sent them:

  - World Bank countries   [metadata, records]  <- array envelope
  - Hacker News search     {"hits": [...], ...} <- dict envelope
  - PokeAPI ditto          one deeply nested entity

Every quirk you have to handle in those three is real. Nothing here is an
invented difficulty; the trailing spaces, the empty strings standing in for
nulls, the numbers arriving as text and the four-levels-down nesting are all
things those APIs actually do.

Nothing needs the network. The tests read from fixtures/, which are recorded
responses. There are live tests too, marked so you can skip them, which hit
the same endpoints to prove your functions work on today's data as well as on
yesterday's recording.

Every docstring shows worked examples in the form `call -> expected result`.
Those lines are the specification — the tests check exactly those cases, so
read them as the contract rather than as decoration.

Run:  python -m pytest test_task.py -v -m "not live"
      python task.py          <- prints a profile of the World Bank response
"""

import json
from pathlib import Path

import requests

HERE = Path(__file__).parent
FIXTURES = HERE.parent / "fixtures"
TIMEOUT = 15
HEADERS = {"Accept": "application/json", "User-Agent": "python-api-course/1.0"}


# --------------------------------------------------------------------------
# The reusable toolkit
# --------------------------------------------------------------------------


def find_records(data):
    """Locate the list of record dicts inside an unknown response.

    Return the list, or [] when there isn't one.

    This is the first thing you run against anything unfamiliar. You have just
    parsed a response and you do not yet know whether the records are sitting
    at the top level, wrapped in a dict envelope, or buried inside an array
    envelope. This function answers that for you so you can stop guessing.

    Handle all of these:

      1. Already a list of dicts          [{...}, {...}]     -> itself
      2. Dict envelope                    {"hits": [...]}    -> the inner list
      3. Array envelope                   [{"page": 1}, [{...}]] -> element 1
      4. Single entity                    {"login": "x"}     -> [] (no list found)
      5. Dict keyed by id                 {"1": {...}}       -> [] (not our job)
      6. Empty / None / a scalar                             -> []

    The rule: return the first value you find that is a NON-EMPTY LIST whose
    first element is a dict. Search the top level, then one level down.

    For a dict envelope with several candidate keys, prefer the LONGEST list
    -- the payload is essentially always bigger than any metadata list.

    Do NOT hardcode key names like "hits" or "results". The whole point is
    that it works on an API you've never seen. Every service names this key
    differently and there is no convention to learn, so you identify the data
    by its shape instead: metadata is scalars, records are dicts.

    The genuinely subtle part is case 3, and it is worth thinking about before
    you write anything. A World Bank payload looks like [{...}, [...]], which
    means it satisfies TWO of the descriptions above at the same time. It is a
    list whose first element is a dict, so case 1 says "this is already your
    answer" and hands back the two-element envelope. It also contains an inner
    list of dicts, so case 3 says "the answer is the 295 records inside." Both
    statements are true of the same object, so whichever test you run first is
    the answer you get -- and only one of them is right. Look inside a list for
    a nested list of records BEFORE you accept the outer list itself.

    Getting that order wrong is nasty precisely because nothing crashes. You
    end up with a record count of 2, a field profile describing pagination
    metadata, and no error message anywhere to suggest you took a wrong turn.
    """
    # TODO
    raise NotImplementedError


def profile_fields(records):
    """Report on every field across a list of records.

    Return {field_name: {"present": int, "null": int, "types": [str, ...]}}

    This is how you find out what the response ACTUALLY contains, as opposed
    to what record zero led you to believe. Real APIs are inconsistent from
    one record to the next, and one pass over the whole list tells you exactly
    where.

    The three numbers, and why each earns its place:

    - present: how many records contain the key at all
    - null:    how many contain it with a value of None
    - types:   sorted distinct type names of the NON-None values

    profile_fields([{"a": 1}, {"a": None, "b": "x"}, {"a": "2"}]) ==
    {
      "a": {"present": 3, "null": 1, "types": ["int", "str"]},
      "b": {"present": 1, "null": 0, "types": ["str"]},
    }

    Present and null are counted separately because they answer two different
    questions. "Present" tells you whether square brackets are safe: a field
    present in fewer records than you have must be read with .get(), or you
    get a KeyError partway through and lose everything you had processed.
    "Null" tells you whether there is any data worth having: a key can be in
    every single record and hold None in most of them, in which case it passes
    the presence test and is still useless to you. Rolling the two together
    into one number would hide whichever problem you happen to have.

    The types list is the third signal, and a list with more than one entry is
    a warning rather than a curiosity. A well-behaved field has exactly one
    type across every record. Two types means either a number that arrives as
    text in some records and as a number in others -- which will silently
    corrupt any sorting or arithmetic you do on it -- or a nested value that is
    a dict when populated and something else when not. Either way you want to
    know before you build on it, not after.

    Note that types describes only the non-None values. Nulls are already
    counted in their own column, and letting "NoneType" into the type list
    would make almost every optional field look inconsistent.
    """
    # TODO
    raise NotImplementedError


def inconsistent_fields(records):
    """Return the sorted names of fields that are NOT present in every record.

    This is profile_fields boiled down to the one answer you most often want:
    the shortlist of fields you cannot trust.

    inconsistent_fields([{"a": 1, "b": 2}, {"a": 3}]) -> ["b"]
    inconsistent_fields([]) -> []

    Anything this returns must be accessed with .get(), never []. Anything it
    does not return is safe with square brackets. Running this before you
    write the flattening code is ten seconds that prevents the crash-on-
    record-700 failure, which is the most annoying way to lose a job that was
    almost finished.

    Sorting the names is not decoration -- it makes the output stable between
    runs, so you can compare it against a previous run and against a test.
    """
    # TODO
    raise NotImplementedError


def walk_paths(data, prefix=""):
    """Return every leaf path in a nested structure, with its value.

    A LIST of (path, value) tuples, in document order. Dicts extend the path
    with ".key"; lists extend it with "[index]". Leaves are anything that is
    not a dict or list -- plus empty dicts and empty lists, which are leaves
    because there is nothing inside them to describe.

    walk_paths({"a": 1, "b": {"c": [10, 20]}}) ->
        [("a", 1), ("b.c[0]", 10), ("b.c[1]", 20)]

    walk_paths({"a": [], "b": {}}) ->
        [("a", []), ("b", {})]

    walk_paths(42) -> [("", 42)]

    This is the "where on earth does that value live" tool. On a response like
    PokeAPI's it turns 800 lines of JSON into a searchable list.

    This function calls itself, which is the only genuinely new mechanic in
    the unit, so here is how to think about it. The function's job is: given an
    object and the path you took to reach it, describe everything inside it. If
    the object is a plain value, that is easy -- there is nothing inside, so you
    report one pair, (prefix, data), and you are done. If it is a dict, you
    cannot answer directly, but you can hand the smaller problem back to
    yourself: for each key, describe whatever is under it, and the path to get
    there is your current prefix plus that key. Same for a list, except the
    path segment is "[index]" rather than ".key".

    The `prefix` parameter is what makes this work. It is the trail of
    breadcrumbs -- the route travelled so far -- and each nested call receives a
    prefix one segment longer than the one it was given. Every call goes one
    level deeper and one segment longer until it reaches something that is not
    a container, and that is where the descending stops. The top-level caller
    passes no prefix at all, which is why the default is the empty string and
    why a scalar at the root reports its path as "".

    One case looks arbitrary and is not: an EMPTY dict or list counts as a
    leaf. The reason is that descending into an empty container produces
    nothing whatsoever, so the path to it would vanish from your index
    entirely -- and "this field is present but empty" is exactly the kind of
    thing you built the index to tell you. There is nothing inside to describe,
    so you describe the container itself. Watch for this: it is the difference
    between the second example above returning two pairs and returning none.
    """
    # TODO
    raise NotImplementedError


def search_paths(data, needle):
    """Return the paths from walk_paths whose PATH contains `needle`.

    Case-insensitive substring match on the path only, not the value.
    Returns a list of (path, value) tuples in document order.

    search_paths({"user": {"name": "x"}, "id": 1}, "name")
        -> [("user.name", "x")]

    Use it as: "I know there's a name in here somewhere, where?"

    This is a thin filter over walk_paths, so build it on top rather than
    writing the traversal a second time. The match is case-insensitive because
    you are typing a guess under time pressure and APIs disagree about whether
    it is "userName" or "username", and it matches on the path rather than the
    value because you are looking for where a FIELD lives, not for a
    particular piece of data.

    The payoff is bigger than it looks. Search the PokeAPI fixture for
    "stat.name" and you get seven hits, not the six visible stats -- the extra
    one lives under past_stats, a field you would never have known was there.
    That is the whole argument for searching instead of scrolling.
    """
    # TODO
    raise NotImplementedError


# --------------------------------------------------------------------------
# Applying the toolkit to real responses
# --------------------------------------------------------------------------


def load_fixture_file(name):
    """Read fixtures/<name>.json. Provided for you -- no TODO here."""
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def flatten_worldbank_countries(payload):
    """Flatten the World Bank country response into clean records.

    The payload is [metadata_dict, list_of_country_dicts]. Each country:

        {"id": "ABW", "iso2Code": "AW", "name": "Aruba",
         "region":      {"id": "LCN", "iso2code": "ZJ", "value": "Latin America & Caribbean "},
         "adminregion": {"id": "",    "iso2code": "",   "value": ""},
         "incomeLevel": {"id": "HIC", "iso2code": "XD", "value": "High income"},
         "capitalCity": "Oranjestad",
         "longitude": "-70.0167", "latitude": "12.5167"}

    Produce, per country:

        {"code": "ABW",
         "name": "Aruba",
         "region": "Latin America & Caribbean",     <- stripped
         "income_level": "High income",
         "capital": "Oranjestad",
         "latitude": 12.5167,                       <- float, not string
         "longitude": -70.0167}

    Every one of the following is something this API actually does, not a rule
    invented to make the exercise harder. Look at the sample record above and
    you can see each of them sitting there.

    Get the list with find_records rather than indexing [1] blindly. You wrote
    that function for exactly this shape, and using it here is the difference
    between code that handles the World Bank and code that handles envelopes
    in general.

    Region and incomeLevel are not strings -- they are nested dicts, and the
    human-readable label is under their "value" key. Reach in defensively;
    unit 04's `or {}` is the tool.

    String values carry trailing spaces. The region really does arrive as
    "Latin America & Caribbean " with a space on the end, and if you group by
    it unstripped you get two buckets that look identical on screen and are not
    equal to Python. Strip every string field.

    Empty string is used where you would expect null, throughout. An aggregate
    row like "World" has no administrative region, so rather than sending null
    the API sends "". That is worse than null because it is still a string and
    sails through any type check, so normalise it to None as it arrives.

    Latitude and longitude arrive as STRINGS, and may be "" for rows that have
    no location. Convert them to floats, and produce None when the conversion
    cannot be made rather than letting it raise.

    capitalCity is "" for aggregates, which should become None by the same
    rule as everything else.

    Aggregate rows (regions, income groups) are mixed in with real countries
    and are kept -- filtering them is the caller's business.
    """
    # TODO
    raise NotImplementedError


def summarize_by_region(countries):
    """Count flattened countries per region, ignoring rows with no region.

    Return a list of (region, count) sorted by count descending, then region
    ascending.

    Pure function -- takes the output of flatten_worldbank_countries.

    This is the payoff for all the cleaning above: once the records are flat
    and the regions are stripped and the blanks are None, a group-by is a
    couple of lines. It is also a small demonstration of why the stripping
    mattered, because an unstripped region would show up here as a separate
    bucket from its stripped twin.

    The two-part sort is deliberate. Count descending is what anybody asking
    the question wants to see. Region ascending as a tiebreaker is what makes
    the output identical from one run to the next, so that two regions with
    the same count do not swap places for no reason and make you wonder what
    changed.

    "Ignoring rows with no region" means rows whose region is None do not
    appear at all -- not as a None bucket, not as an empty-string bucket.
    """
    # TODO
    raise NotImplementedError


def flatten_hn_hits(payload):
    """Flatten a Hacker News Algolia search response.

    The payload is a dict envelope. Real data lives under "hits"; find it with
    find_records rather than by name.

    Each hit has (among ~15 fields):
        {"objectID": "45751400", "title": "...", "author": "...",
         "points": 512, "num_comments": 288, "url": "https://...",
         "created_at": "2025-10-24T13:22:33.000Z",
         "_tags": [...], "_highlightResult": {...}, "story_text": null, ...}

    Produce, per hit:
        {"id": <objectID as a string>,
         "title": <title, or "" when null>,
         "author": <author, or None>,
         "points": <int, 0 when missing or null>,
         "comments": <num_comments as int, 0 when missing or null>,
         "domain": <host part of url, lowercase, or None when url is null>,
         "date": <the first 10 chars of created_at, or None>}

    Notes on the real data. "url" is null for Ask HN and Show HN posts, which
    are text rather than links, so any code that assumes a URL exists will die
    on the first one of those it meets. "title" is null on comment-type
    records for the same kind of reason.

    Dropping _highlightResult and _tags is deliberate, and worth a sentence
    because the beginner instinct is to keep everything just in case. Those two
    fields are search-engine internals -- Algolia's record of which substrings
    matched your query, and its own tagging scheme -- not data about the story.
    Carrying them means every row you print is unreadable and every CSV you
    write has a column of nested markup in it. Seven useful fields beat fifteen
    fields of which eight are noise.

    Note also that you are renaming as you go: num_comments becomes comments,
    objectID becomes id, and a whole URL becomes just its domain. Once you
    flatten, the field names are yours, and picking good ones is free.

    You may reuse extract_domain logic from unit 02, or use urllib.parse.
    """
    # TODO
    raise NotImplementedError


def pokemon_profile(payload):
    """Reduce a PokeAPI /pokemon/<name> response to a flat profile.

    The response is one entity with ~20 top-level keys and several levels of
    nesting. You want:

    {
      "name": payload["name"],
      "id": payload["id"],
      "height": payload["height"],
      "weight": payload["weight"],
      "types": ["normal"],                 # from types[].type.name, in slot order
      "abilities": ["limber", "imposter"], # from abilities[].ability.name, slot order
      "stats": {"hp": 48, "attack": 48, ...},   # stats[].stat.name -> base_stat
      "total_stats": <sum of the stat values>,
    }

    Every list may be empty or absent; nothing may crash.

    The reach for a type name is payload -> types -> [i] -> type -> name: four
    steps, each of which can hand you None or a missing key, and it is exactly
    the kind of traversal that trips people up live. Do it carefully and one
    level at a time. Guard the list before you loop over it, and guard each
    nested dict before you read a key out of it. Chasing four levels in a
    single unguarded expression is how you end up staring at "NoneType object
    is not subscriptable" with someone watching.

    Slot ordering: sort types by their "slot" key and abilities by their "slot"
    key, since the API does not promise array order matches slot number. That
    is the important word -- does not promise. The array might well arrive in
    slot order most of the time, and code that relies on it will look correct
    for a long while and then quietly report a Pokemon's secondary type as its
    primary one. The slot number is the API telling you the real order in
    writing; use it rather than trusting the accident of how the list was
    serialised.

    total_stats is the sum of the values in your stats dict, which means an
    empty payload has to produce 0 rather than raising or returning None.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    payload = load_fixture_file("worldbank_countries")
    records = find_records(payload)
    print(f"{len(records)} records found\n")

    for field, info in profile_fields(records).items():
        print(f"{field:>14}  present={info['present']:>4}  types={info['types']}")

    print("\ninconsistent:", inconsistent_fields(records))

    countries = flatten_worldbank_countries(payload)
    print("\ntop regions:")
    for region, count in summarize_by_region(countries)[:5]:
        print(f"  {count:>4}  {region}")
