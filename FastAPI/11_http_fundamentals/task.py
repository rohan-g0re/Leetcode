"""Unit 11 task — HTTP fundamentals, without the network.

Nothing in this file calls a server. Every function here is URL and header
manipulation done with Python's standard library, and that is the point: each
one is a job the `requests` library will do for you invisibly in unit 12. You
are writing them once, by hand, so that the library stops being a black box and
so that when a call misbehaves you know which layer to look at.

The tool you need is `urllib.parse`, a module that ships with Python and exists
purely to take URLs apart and put them back together. You have never met it, so
here is the shape of it. `urlparse(url)` reads a URL and hands back a named
tuple — a tuple whose positions also have names — with the pieces from the
lesson available as fields: `.scheme`, `.netloc` (the host), `.path`, `.query`,
`.fragment`. `parse_qsl(query)` takes the raw query string and returns a list of
`(key, value)` pairs, decoding any percent-escapes on the way. `urlencode(d)`
goes the other way, turning a dictionary into a correctly encoded query string.
And `urlunparse(parts)` reassembles a full URL from those five pieces plus a
sixth you can ignore. Look each of them up as you go; two minutes in the
interactive prompt with a real URL is worth more than reading about them.

Every function's docstring shows worked examples in the form
`call -> expected result`. Those lines are the specification — the tests check
exactly those cases, so read them as the contract rather than as decoration.

Run:  python -m pytest test_task.py -v
"""

from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


def split_url(url):
    """Break a URL into its parts.

    Take a URL as one long string and hand back its five pieces as a dictionary
    you can actually inspect. The query string comes back already parsed into a
    dictionary of its own rather than left as raw text.

    Return a dict with exactly these keys:
        scheme, host, path, query (a dict), fragment

    split_url("https://api.github.com/users/x?a=1&b=2#top") ->
        {"scheme": "https",
         "host": "api.github.com",
         "path": "/users/x",
         "query": {"a": "1", "b": "2"},
         "fragment": "top"}

    split_url("https://api.github.com") ->
        {"scheme": "https", "host": "api.github.com",
         "path": "", "query": {}, "fragment": ""}

    A repeated parameter keeps the LAST value:
        "?a=1&a=2"  ->  {"a": "2"}

    Percent-encoded values must come back decoded:
        "?q=hello%20world" -> {"q": "hello world"}

    urlparse gives you a named tuple; parse_qsl turns a query string into
    (key, value) pairs.

    Why bother: this is the diagnostic you reach for when a request is going
    somewhere you did not intend. Printing a URL tells you very little, because
    it is one dense string; printing its parts tells you immediately that your
    host is wrong, or that a parameter you thought you added is missing. Notice
    also that the second example returns empty strings rather than None for the
    missing path and fragment — that is what urlparse itself does, and it means
    you can go on calling string methods on the result without checking first.

    Two things worth understanding rather than copying. parse_qsl returns a
    LIST of pairs rather than a dictionary, because a query string is genuinely
    allowed to repeat a key — "?a=1&a=2" is legal and carries two values. A
    dictionary cannot hold both, so parse_qsl refuses to make that decision for
    you and hands back everything it found. Turning that list into a dict is
    you choosing the "last one wins" rule, which is what the third example
    specifies. And the percent-decoding in the fourth example is free: parse_qsl
    undoes the encoding from the lesson without being asked, which is exactly
    the asymmetry that makes hand-built query strings so dangerous — encoding
    is the step people skip, decoding is the step that happens automatically.
    """
    # TODO
    raise NotImplementedError


def add_params(url, **new_params):
    """Return the url with extra query parameters added or replaced.

    Given a URL that may already carry a query string, produce a new URL with
    the parameters you name added, overwritten, or deleted — without disturbing
    anything else about it.

    add_params("https://x.com/a?p=1", q="hi")   -> "https://x.com/a?p=1&q=hi"
    add_params("https://x.com/a?p=1", p=2)      -> "https://x.com/a?p=2"
    add_params("https://x.com/a", q="a b")      -> "https://x.com/a?q=a+b"
    add_params("https://x.com/a", q=None)       -> "https://x.com/a"

    Rules:
      - existing params are preserved unless overridden by name
      - params with a value of None are REMOVED (or stay absent)
      - values are properly encoded -- urlencode handles this; do not build
        the string yourself
      - existing params keep their original order; new ones are appended
      - the fragment is preserved

    Note the third example: urlencode encodes a space as "+" in a query
    string, which is correct and equivalent to %20 there.

    Why bother: this is the single most useful URL helper there is, because
    "now fetch page two" and "now filter to Python repositories" are the two
    things you are always asked next. Doing it with string concatenation means
    working out whether the URL already has a "?" or needs an "&", and then
    getting the encoding right, and then not clobbering the fragment. Doing it
    by parsing, editing a dictionary, and reassembling is both shorter and
    correct for inputs you did not think of.

    The None rule is deliberate and more useful than it looks. It lets a caller
    pass every option in one call and simply set the ones it does not want to
    None, instead of building a filtered dictionary first. You will see the same
    convention in `requests`, which drops any parameter whose value is None.

    The signature uses `**new_params`, the syntax from unit 06 that collects any
    keyword arguments the caller supplies into a dictionary. So the parameters
    arrive already in a dictionary and already in the order they were written,
    which is why "new ones are appended" falls out naturally.
    """
    # TODO
    raise NotImplementedError


def join_path(base, *parts):
    """Join a base URL with path segments, safely.

    Stick path segments onto the end of a base URL and get back something that
    is actually valid, whatever combination of leading and trailing slashes the
    caller happened to supply.

    join_path("https://x.com", "users", "torvalds")
        -> "https://x.com/users/torvalds"
    join_path("https://x.com/api/", "/users/", "/torvalds/")
        -> "https://x.com/api/users/torvalds"
    join_path("https://x.com/api?k=1", "users")
        -> "https://x.com/api/users?k=1"
    join_path("https://x.com")
        -> "https://x.com"

    Stray slashes on either side of a segment must not produce "//".
    An empty or None segment is skipped entirely.
    Any query string on the base is preserved and stays at the end.

    Why bother: the moment you have a base URL in one variable and a username
    in another, you are going to write base + "/" + name, and it will work
    until the day the base already ends in a slash. Then you send a request to
    a path containing "//", which most servers treat as a different path
    entirely, and you get a 404 for a resource that certainly exists. Handling
    the slashes in one place means never thinking about it again.

    The third example is the one that shows why you should not treat the URL as
    plain text. If you append "users" to the end of "https://x.com/api?k=1" as
    a string, you get "...?k=1users" and the query parameter is silently
    corrupted. Pulling the URL apart, changing only the path, and putting it
    back means the query travels along untouched — which is the general lesson
    of this whole file.

    The `*parts` in the signature is unit 06's other collecting syntax: it
    gathers however many positional arguments follow `base` into a tuple, so
    callers can pass one segment or six.
    """
    # TODO
    raise NotImplementedError


def classify(status):
    """Return a dict describing an HTTP status code.

    Given a status code, report what kind of code it is and, more importantly,
    what you should do about it.

    {
      "code": <int>,
      "category": "success" | "redirect" | "client_error" | "server_error"
                  | "informational" | "unknown",
      "retryable": <bool>,
      "our_fault": <bool>,
    }

    retryable: True for 429 and any 5xx. False otherwise.
    our_fault:  True for any 4xx (including 429). False otherwise.

    classify(200) -> {"code":200,"category":"success","retryable":False,"our_fault":False}
    classify(429) -> {"code":429,"category":"client_error","retryable":True,"our_fault":True}
    classify(503) -> {"code":503,"category":"server_error","retryable":True,"our_fault":False}
    classify(42)  -> {"code":42,"category":"unknown","retryable":False,"our_fault":False}

    Note 429 lands in client_error by range but is still retryable -- that
    combination is the whole reason this function returns a dict instead of
    a single label.

    Why bother, and read this bit properly, because it is the point of the
    function. The obvious design is to return one word — "success", "retry",
    "give up" — and it does not survive contact with reality. 429 means "too
    many requests." Its first digit is a 4, so by the lesson's rule it is a
    client error and the fault is yours: you sent too many. But unlike every
    other 4xx, sending the identical request again *will eventually work*, once
    you have waited. So 429 is simultaneously your fault and worth retrying,
    and no single label can say both.

    That is why the answer is a dictionary with two independent booleans
    instead of one string. "Whose fault is it" and "should I try again" turn out
    to be different questions, and the codes that answer them differently are
    exactly the ones that matter operationally. When you build retry logic in
    unit 15, `retryable` is the flag it will branch on.

    One boundary to get right: the categories cover 100 through 599, so
    "unknown" is only for codes below 100 or 600 and above. 100-199 is
    "informational", which you will never see in practice but still has a name.
    """
    # TODO
    raise NotImplementedError


def build_auth_headers(token=None, api_key=None, user_agent="python-course/1.0"):
    """Build a request header dict.

    Assemble the dictionary of headers you would attach to a request, including
    credentials only when you actually have them.

    Always includes:
        "Accept": "application/json"
        "User-Agent": <user_agent>

    Adds "Authorization": f"Bearer {token}"  when token is given.
    Adds "X-API-Key": api_key                when api_key is given.

    build_auth_headers() ->
        {"Accept": "application/json", "User-Agent": "python-course/1.0"}

    Empty strings count as not given.

    Why bother: the two always-present headers are not filler. "Accept" tells
    the server you want JSON rather than XML or HTML, and "User-Agent" names
    your program — which GitHub flatly requires, refusing any request that
    omits it. Having one function that produces a correct header dictionary
    means you never send a request that is missing either of them.

    The "empty strings count as not given" rule is unit 01's truthiness doing
    real work. An empty string is falsy, so a plain `if token:` treats both
    None and "" as absent, which is what you want: an empty token is not a
    token, and sending "Authorization: Bearer " with nothing after it earns you
    a confusing 401 rather than an honest anonymous request. Reaching for
    `is not None` here would let the empty string through.

    And note what this function does NOT do: it does not know where the token
    came from. That is deliberate. Credentials get read from an environment
    variable at the edge of your program and passed in — they never appear in
    source code, for the reasons in the lesson.
    """
    # TODO
    raise NotImplementedError


def parse_link_header(value):
    """Parse an HTTP Link header into {rel: url}.

    GitHub returns pagination this way. A real value looks like:

    <https://api.github.com/user/repos?page=2>; rel="next",
      <https://api.github.com/user/repos?page=50>; rel="last"

    (all on one line -- wrapped here for readability)

    parse_link_header(that) ->
        {"next": "https://api.github.com/user/repos?page=2",
         "last": "https://api.github.com/user/repos?page=50"}

    parse_link_header("")    -> {}
    parse_link_header(None)  -> {}

    Rules:
      - entries are separated by ", "  (a comma; there may be spaces around it)
      - each entry is "<url>; rel=\"name\""
      - there may be extra parameters after rel -- ignore them
      - be tolerant of extra whitespace
      - malformed entries are skipped rather than raising

    This is real parsing of a real header, and it is exactly what you would
    write in an interview when you notice the response is paginated.

    Why bother: when a GitHub response has more results than fit in one page,
    this header is how the server tells you where the rest are. `rel` is short
    for "relation" and names what each URL is relative to the one you just
    fetched — "next", "prev", "first", "last". Following the "next" link is
    strictly better than incrementing a page number yourself, because the
    server has already worked out the correct URL including every filter you
    sent, and it simply stops offering a "next" when you reach the end.

    The interesting engineering question is how to split it up. The obvious
    move is to split the string on commas and handle each piece. Resist it: a
    URL is perfectly entitled to contain a comma, and one will, and then your
    split cuts a URL in half and produces two pieces of nonsense. The robust
    route is a regular expression — a small pattern language for describing the
    shape of text, available in Python's `re` module — which lets you say "find
    something in angle brackets, then a semicolon, then rel= and a name" and
    have it scan the whole string finding every match. Entries that do not fit
    the shape simply never match, which is how the malformed-input rule gets
    satisfied without you writing any error handling at all. The hints file has
    the pattern if you get stuck; try to build one first.
    """
    # TODO
    raise NotImplementedError


def next_page_url(link_header):
    """Return the "next" URL from a Link header, or None when there isn't one.

    One line, using parse_link_header.

    Why bother: this is the function your paging loop actually calls. It turns
    the previous function's dictionary into the one question a loop wants to
    ask — "is there another page, yes or no?" — and returning None for "no"
    means the loop condition writes itself. The reason it is one line is that
    the hard work is already done; the value here is having the right small
    piece with the right name.
    """
    # TODO
    raise NotImplementedError


def seconds_until_reset(headers, now_epoch):
    """Work out how long to wait, from rate-limit headers.

    Given the headers from a response that told you to slow down, decide how
    many seconds to sleep before trying again.

    `headers` is a dict of response headers (keys may be in ANY case).
    `now_epoch` is the current time as a Unix timestamp (an int).

    Rules, in priority order:
      1. If "Retry-After" is present and is an integer number of seconds,
         return that integer.
      2. Otherwise, if "X-RateLimit-Remaining" is "0" and "X-RateLimit-Reset"
         holds a Unix timestamp, return reset - now_epoch, never below 0.
      3. Otherwise return 0.

    seconds_until_reset({"Retry-After": "30"}, 1000)                    -> 30
    seconds_until_reset({"X-RateLimit-Remaining": "0",
                         "X-RateLimit-Reset": "1100"}, 1000)            -> 100
    seconds_until_reset({"x-ratelimit-remaining": "5"}, 1000)           -> 0
    seconds_until_reset({}, 1000)                                        -> 0

    The case-insensitivity is not busywork: real servers send
    "Retry-After", "retry-after", and "RETRY-AFTER" and your code has to
    cope with all three.

    Why bother: this is the arithmetic behind every polite retry. The server
    has told you to stop; this function converts that into a number of seconds,
    and everything downstream just sleeps for it. Returning 0 for "you are not
    limited" means the caller needs no special case — it always asks, always
    sleeps for the answer, and usually sleeps for nothing.

    Two details are doing real teaching here. First, the case-insensitivity.
    Header names are case-insensitive by the standard, so all three spellings
    above are equally correct and you cannot predict which you will get. The
    `requests` library shields you from this entirely: the object it hands back
    is a special case-insensitive dictionary, so any spelling works. The plain
    dict this function receives is NOT that object — it is what a test fixture,
    a log file, or a hand-built example gives you — so you have to normalise the
    keys yourself before you look anything up. Doing that once, at the top, is
    far better than trying three spellings at every lookup.

    Second, "Retry-After" is allowed to hold either a number of seconds or an
    HTTP date, and rule 1 only claims the number form. So the conversion to an
    integer can legitimately fail on well-formed input, and when it does you
    should fall through to rule 2 rather than crash. That is unit 08's
    try/except earning its keep on a case that is not an error at all, just a
    format you have chosen not to support.

    And the timestamp trap from the lesson: "X-RateLimit-Reset" is an absolute
    Unix timestamp — seconds since 1 January 1970 — not a countdown. You get a
    duration by subtracting `now_epoch` from it, and you clamp the result at
    zero because the reset moment may already have passed.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    print(split_url("https://api.github.com/users/x?a=1&b=2#top"))
    print(add_params("https://api.github.com/search?q=py", page=2, sort=None))
    print(classify(429))
