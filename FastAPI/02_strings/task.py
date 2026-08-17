"""Unit 02 task — text.

There are seven functions here and none of them are invented puzzles. Each one
is a job you will actually have to do to data that arrived from an API: tidying
up field names so they can become columns, pulling a date apart, shortening text
so it fits on a screen, finding the host inside a URL, assembling the question
marks and ampersands at the end of a request, pulling keywords out of a title,
and printing a row that lines up with the row above it.

Four of them (normalize_key, parse_iso_date, extract_domain and
build_query_string) are hand-built versions of things a library will do for you
later in the course. That is on purpose. Writing them once by hand means that
when the library does it, you know what it is doing and you can tell when it has
done something you did not want.

Work top to bottom. Each function is independent, so if one is fighting you,
move on and come back. Open hints.md only after about ten minutes of real
effort on a function — the struggle before the hint is where the learning is.

Run:  python -m pytest test_task.py -v
"""


def normalize_key(raw):
    """Take a messy field name and hand back a tidy one.

    You are given one piece of text — a field name exactly as some API wrote it,
    stray spaces and capital letters and all — and you return the same name
    rewritten in the plain, predictable style Python code likes: all lowercase,
    words separated by single underscores. That style has a name, snake_case,
    and you will see it everywhere from here on.

    normalize_key("  First Name ")  -> "first_name"
    normalize_key("User-ID")        -> "user_id"
    normalize_key("total   count")  -> "total_count"
    normalize_key("API_Key")        -> "api_key"
    normalize_key("")               -> ""

    Those five lines are the specification — the tests check exactly them, so
    read them before you write anything. In words, the rules are: remove any
    spaces at the very start and very end, make everything lowercase, turn any
    stretch of spaces or hyphens (however long) into one single underscore, and
    leave underscores that were already there alone.

    Why bother. Think of a field name as a column name in a table you are about
    to build. Different APIs, and sometimes different endpoints of the same API,
    will hand you "First Name", "first-name" and "first_name" for the identical
    piece of information. If you keep them as they arrive you end up with three
    columns that are secretly one column, and every count and join you do
    afterwards is quietly wrong. Cleaning names on the way in means nothing
    downstream ever has to think about it again. In SQL terms this is the
    equivalent of settling on one naming convention before you create the table
    rather than after.

    Where to start. Look up what `.split()` does when you call it with no
    argument at all — it has a specific and very convenient behaviour with runs
    of whitespace that does most of this job for you. Then think about what to
    do with hyphens so that they get swept up by the same mechanism, and note
    that whatever you do to them has to happen before the split, not after.
    """
    # TODO
    raise NotImplementedError


def parse_iso_date(text):
    """Pull the year, month and day out of a date written as text.

    Dates almost never arrive from an API as anything Python understands as a
    date. They arrive as text, in a layout called ISO-8601, which is the
    international standard that puts the year first: "2024-01-05". Sometimes the
    same field also carries a time, glued on after a capital "T". Your job is to
    hand back the three numbers, or to say clearly that you could not.

    parse_iso_date("2024-01-05")            -> (2024, 1, 5)
    parse_iso_date("2024-01-05T10:30:00Z")  -> (2024, 1, 5)
    parse_iso_date("not a date")            -> None
    parse_iso_date("")                      -> None
    parse_iso_date(None)                    -> None

    Notice that the first two lines are the same field from the same API in the
    real world — one record has a time attached and the next one does not — so
    you have to cope with both. When it works, return a tuple of three whole
    numbers: a tuple is just a fixed row of values written in parentheses, and
    the numbers must be actual numbers, so (2024, 1, 5) and not ("2024", "01",
    "05"). When it does not work, return None, Python's word for "nothing here."

    Be strict about what counts as a date. Cut off anything from the "T"
    onwards, and then the part you are left with must be exactly three pieces
    separated by hyphens, with every piece made entirely of digits. Anything
    else is a None. Being strict is the point: a function that half-believes
    bad input is worse than one that refuses it, because the wrong answer
    travels further before anyone notices.

    Why write this by hand. Python's datetime module parses ISO dates in one
    line and in real work you would use it. But it also throws an exception on
    input it dislikes, and you cannot decide what to do about that until you
    have felt what "unparseable" actually means. So do this one with string
    operations only — no datetime — and you will understand exactly what the
    library is doing for you when you meet it later.

    Where to start. Two questions get you most of the way: how do you chop a
    string at a character, and how do you ask a string whether it is all digits?
    Both are string methods from the lesson. Also decide early what you do when
    the input is not text at all — that None case in the examples is there to
    make you handle it deliberately rather than crash.
    """
    # TODO
    raise NotImplementedError


def truncate(text, limit):
    """Shorten text so it fits, and show that you shortened it.

    You get a piece of text and a maximum length. If the text already fits, hand
    it back untouched. If it does not, cut it down and end it with three dots so
    a reader can see something was removed. The dots count towards the limit —
    they are part of the result, not extra — which means the string you return
    is never longer than `limit`, no matter what you were given.

    truncate("hello world", 8)  -> "hello..."
    truncate("hello", 8)        -> "hello"
    truncate("hello", 5)        -> "hello"
    truncate("hello", 4)        -> "h..."
    truncate("hello", 3)        -> "..."
    truncate("hello", 2)        -> ".."

    Read that last line twice, because it looks like a mistake and is not. With
    a limit of 2 there is no room for even the three dots, so you get two of
    them. It is a strange-looking output, but it keeps the one promise this
    function makes — the result is always `limit` characters or fewer — true in
    every single case, with no exceptions to remember.

    Why this exists. The moment you print a list of API records to a terminal,
    one of them will have a description four hundred characters long and your
    neat output turns into a wall of wrapped text. Truncating is what keeps a
    printed table readable, and "never longer than the limit, ever" is what
    lets you rely on the column widths you chose.

    Where to start. Slicing is the tool, and the useful fact about it from the
    lesson is that it never raises an error — asking for more characters than
    exist just gives you what is there. Work out how many characters of the
    original you are allowed to keep once the dots have taken their share, then
    think separately about what happens when that number goes to zero or below.
    """
    # TODO
    raise NotImplementedError


def extract_domain(url):
    """Find the server name inside a URL, in lowercase.

    A URL has a fixed shape: a scheme like "https", then "://", then the host —
    the name of the machine being asked — and then optionally a path starting
    with "/" and a query starting with "?". You want the host and nothing else,
    converted to lowercase, or None if what you were handed is not a URL at all.

    extract_domain("https://api.github.com/users/x")  -> "api.github.com"
    extract_domain("http://Example.COM/a/b?c=1")      -> "example.com"
    extract_domain("https://site.org")                -> "site.org"
    extract_domain("ftp://files.net/x")               -> "files.net"
    extract_domain("not a url")                       -> None
    extract_domain("")                                -> None

    So the pattern you are matching is "<scheme>://<host>[/<rest>][?<query>]".
    The test for "is this a URL" is simply whether "://" appears in it; if it
    does not, return None. The lowercasing matters because host names are
    officially case-insensitive, so "Example.COM" and "example.com" are the same
    machine — and if you do not normalize them, counting requests per host gives
    you two rows where there should be one. That is the same lowercase-before-
    you-compare habit from the lesson, showing up in real work.

    Why write this by hand. Python ships urllib.parse, which does this properly
    and handles ports, usernames and every strange corner of the URL standard;
    unit 13 uses it and so should you in real code. Doing it manually once tells
    you which pieces a URL is made of, which is what you need when an API's
    documentation talks about "the base URL" and "the path" and expects you to
    know the difference.

    Where to start. Get to the text after "://" first, then work out where the
    host ends. It stops at the first "/" or the first "?", whichever turns up
    sooner — and in "https://site.org" neither turns up at all, so it runs to
    the end of the string. Splitting on one character and taking the first piece
    handles the "or it just ends" case for free; do that twice and you are done.
    """
    # TODO
    raise NotImplementedError


def build_query_string(params):
    """Build the "?q=python&page=2" part of a URL from a set of settings.

    You are handed a dict — a collection of labelled values, written with curly
    braces, which unit 04 covers properly; for now just read {"q": "python"} as
    "the setting named q has the value python". Your job is to flatten it into
    the text that goes on the end of a URL, where each setting is written as
    name=value and the settings are separated by "&".

    build_query_string({"q": "python", "page": 2})  -> "q=python&page=2"
    build_query_string({})                          -> ""
    build_query_string({"a": None, "b": 1})         -> "b=1"

    The rules in sentences. Any setting whose value is None is left out of the
    result entirely. Values that are not text — the 2 in the first example — get
    converted to text. The finished pairs are joined with "&" in the order the
    dict already has them. And you do not need to worry about escaping awkward
    characters like spaces here; the requests library handles that in real code.

    Watch the None rule carefully, because there is a trap in it. Dropping
    "values that are None" is not the same as dropping "values that are empty
    or zero." A page number of 0 and a search term of "" are both real settings
    that the caller deliberately asked for, and they must survive. Python has a
    specific way to ask "is this literally None" as opposed to "is this
    empty-ish", and this is exactly the situation it is for. There is a test
    waiting for you if you get it wrong.

    Why this exists. This is how optional filters actually get built. You write
    one dict with every filter the endpoint supports, leave the ones the user
    did not ask for as None, and they simply vanish from the request instead of
    being sent as empty and confusing the server. The requests library does this
    assembly for you from unit 12 onward; building it once means you know what
    it is producing and can read a URL in a log file and understand it.

    Where to start. Make a list of the "name=value" pieces you want, skipping
    the ones you are dropping, and then join that list with "&". Remember from
    the lesson that join is called on the separator and refuses anything that is
    not text, so the converting has to happen before the joining.
    """
    # TODO
    raise NotImplementedError


def title_words(text, min_length=4):
    """Pick the meaningful words out of a title.

    Given a line of text, return the words worth paying attention to: lowercase,
    with punctuation stripped off, with the very short ones thrown away, with
    duplicates removed, and sorted alphabetically. "Worth paying attention to"
    is defined here purely by length — a word counts if it is at least
    `min_length` characters long once its punctuation has been removed. That
    default of 4 is deliberately crude, and it works surprisingly well, because
    the words it throws away are mostly "a", "the", "for" and "of".

    title_words("Show HN: A tool for parsing JSON, fast!")
        -> ["fast", "json", "parsing", "show", "tool"]
    (dropped: "HN" and "A" are too short, "for" is only 3 characters)

    title_words("a b c", min_length=1)
        -> ["a", "b", "c"]

    Step by step, that means: break the text apart on whitespace; from each
    piece remove any of the characters .,!?:;"'()[] found at either end;
    lowercase what is left; discard it if it is now shorter than `min_length`;
    and finally return what remains with duplicates removed, in alphabetical
    order. Measure the length after stripping, not before — "JSON," is five
    characters with the comma and four without, and the comma is not a word.

    Why this exists. Hand an interviewer a list of two hundred article titles
    from a news API and the obvious question is "what are these about?" This is
    the cheapest possible answer to that: strip the words down, count them, and
    look at the top ten. Real keyword extraction is a large subject, but this
    version takes five minutes and is genuinely informative, and knowing that
    the crude version is available saves you from freezing when asked to say
    something about text you have not read.

    Where to start. Two facts do most of the work. First, `.strip()` will take
    a string of characters as an argument and remove any of them from both ends
    of a word, in any order and any number of times — so you can pass the whole
    punctuation list at once. Second, a set is Python's collection that refuses
    to hold the same thing twice, so putting your words into one removes
    duplicates automatically, and `sorted()` turns a set back into an ordered
    list. Also make sure your loop can cope with a word that strips down to
    nothing at all.
    """
    # TODO
    raise NotImplementedError


def format_table_row(cells, widths):
    """Print one row of a table so that it lines up with the rows around it.

    You get two lists: the values to put in this row, and how wide each column
    should be. Every value is placed on the left of its column and padded with
    spaces out to that column's width, the columns are separated by " | ", and
    any spaces left dangling off the right-hand end of the finished row are
    removed.

    format_table_row(["ab", "c"], [5, 3])   -> "ab    | c"
    format_table_row(["abcdef"], [3])       -> "abcdef"

    Walk through the first example, because the spaces are hard to count by eye.
    "ab" padded out to 5 characters is "ab   ". Then the separator " | ". Then
    "c" padded out to 3 is "c  ". Glue those together and you have "ab    | c  "
    — and then the trailing spaces come off the end, leaving "ab    | c".

    The second example shows the rule for a value that does not fit: you leave
    it alone. Widths are a minimum, not a maximum. A too-long value pushes that
    one row out of alignment, which looks slightly wrong but is honest; silently
    chopping it would hide data, and hidden data is worse than an untidy line.
    If you do want it cut, that is what `truncate` above is for, and calling
    them in that order is a deliberate choice you get to make.

    Why bother. Aligned output is the difference between a wall of numbers and
    something a person can read at a glance, and as the lesson said, an
    interviewer watching your screen registers it. It costs you one function and
    about thirty seconds.

    Where to start. The f-string alignment codes from the lesson do the padding,
    and the useful trick is that the width does not have to be typed in — you
    can supply it from a variable by putting it in its own braces, as in
    f"{value:<{width}}". To walk two lists side by side, look up `zip`, which
    pairs up the first item of each, then the second, and so on. Then join and
    tidy the end.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    print(normalize_key("  User-ID "))
    print(parse_iso_date("2024-01-05T10:30:00Z"))
    print(format_table_row(["ab", "c"], [5, 3]))
