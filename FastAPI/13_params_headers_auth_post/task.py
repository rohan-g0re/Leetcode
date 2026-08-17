"""Unit 13 task — params, headers, auth, POST.

Eight functions. The first four are about controlling a request: what you send
up, and how you read what comes back. The last four point that machinery at two
real endpoints and make you reshape their awkward answers into the shape unit
04 said everything should end up in — a list of flat dictionaries, one per row.

Three APIs are involved, none of which needs a key or an account:
  - jsonplaceholder.typicode.com  (accepts POST, stores nothing)
  - api.open-meteo.com            (weather, date-range params)
  - api.frankfurter.dev           (FX rates, date range in the PATH)

Most of the tests never touch the network. They replace `requests.get` and
`requests.post` with fakes that record what you sent and hand back a canned
response, so you can check your request-building without waiting on anyone's
server. Two of them go further and replace `task.get_json` itself with a
function returning a recorded response. That substitution only works if
`daily_weather` and `fx_series` call `get_json` as a plain module-level name at
the moment they need it. If you "helpfully" copy it into a local variable or
import it under another name, you capture the real function before the test can
swap it out, and those two tests will fail for reasons that look nothing like
the actual cause.

Run the offline tests, then all of them including the live ones:

    python -m pytest test_task.py -v -m "not live"
    python -m pytest test_task.py -v

Run directly for a live demo:
    python task.py

Heads up on api.frankfurter.dev: it sleeps when idle, so the FIRST request
after a quiet period can take ~20 seconds or come back as a 522. Hit it again
and it answers in under a second. That is a genuine, common piece of real-world
API behaviour -- and precisely the problem unit 15 solves with retries and
backoff. Until then, if a live test fails on Frankfurter, just run it again.
"""

import json
import os

import requests

TIMEOUT = 25
PLACEHOLDER = "https://jsonplaceholder.typicode.com"
OPEN_METEO = "https://api.open-meteo.com/v1/forecast"
FRANKFURTER = "https://api.frankfurter.dev/v1"


def build_headers(user_agent="python-api-course/1.0", token_env="API_TOKEN"):
    """Build request headers, taking the bearer token from the environment.

    Build and return a dictionary of headers to attach to a request. Two of
    them go in every time:

        "Accept": "application/json"
        "User-Agent": <user_agent>

    `Accept` tells the server which format you would like back. `User-Agent`
    says who is calling; some APIs reject requests without one, and a
    recognisable value is simply good manners.

    Then the conditional part. If the environment variable named by
    `token_env` is set AND non-empty, also include
    "Authorization": f"Bearer {value}". If it is unset, or set to an empty
    string, leave the Authorization header out entirely rather than sending an
    empty one — an empty credential is worse than no credential, because it
    turns "not authenticated" into "authentication failed".

    Notice what this function does NOT do: it never takes a token as an
    argument, and no token appears anywhere in this file. It reads
    os.environ at call time. That is the entire point of the function. A
    credential written into source is a credential you have published the
    moment the file is committed or shared, and reading it from the
    environment instead costs one line.
    """
    # TODO
    raise NotImplementedError


def clean_params(**params):
    """Drop parameters that carry no information, and normalize the rest.

    This is the one place where you decide, once, how Python values turn into
    query parameters — so that every function below can just hand you a
    dictionary and stop thinking about it.

    Rules:
      - a value of None is dropped
      - an empty string or whitespace-only string is dropped
      - an empty list is dropped
      - a non-empty list is joined with commas into a single string
      - a bool becomes the lowercase string "true"/"false"
        (many APIs reject Python's "True")
      - everything else passes through unchanged
      - 0 and False are NOT dropped -- they are real values

    clean_params(q="py", page=None, sort="")        -> {"q": "py"}
    clean_params(daily=["a", "b"])                  -> {"daily": "a,b"}
    clean_params(current=True, page=0)              -> {"current": "true", "page": 0}
    clean_params(tags=[])                           -> {}

    Careful with the bool rule: isinstance(True, int) is True, so check for
    bool before you check for anything numeric.

    That ordering warning is the whole exercise, so take it seriously. Python
    implements booleans as a special kind of integer, which means True passes
    an integer check and would be swallowed by a numeric branch before your
    bool branch ever runs — and it would go out as the text "True", which is
    exactly the failure the lesson warned about. Put the bool check first. You
    have met this before: it is the same ordering trap as unit 01's
    coerce_number and unit 08's validate_page_size.

    The other rule worth understanding rather than memorising is why 0 and
    False survive while None and "" are dropped. None and "" mean "the caller
    did not give me a value" — there is nothing to send. But 0 is a value. A
    page number of 0 is real, and an interviewer asking for the first page of
    results gets page 1 back if you drop it, with no error, no warning and
    nothing in the output to hint that the request you sent was not the
    request you meant. Silently wrong beats loudly broken only in the sense
    that it takes far longer to find.

    A `**params` signature means the caller passes keyword arguments and you
    receive them collected into a dictionary named `params` — so a call like
    clean_params(q="py") arrives here as {"q": "py"}. Unit 06 covers the
    syntax; for now, treat `params` as an ordinary dictionary and build a new
    one to return.
    """
    # TODO
    raise NotImplementedError


def get_json(url, params=None, headers=None, timeout=TIMEOUT):
    """GET and return parsed JSON, raising on HTTP errors.

    Same as unit 12's fetch_json, but headers are passed in rather than
    hardcoded -- so it can be pointed at any API.

    Three steps and no cleverness: make the GET with whatever params, headers
    and timeout you were given, call raise_for_status() so that a 4xx or 5xx
    becomes a Python exception rather than a response you might mistake for
    data, and return response.json().

    Every function below that reads data goes through here, which is exactly
    why the tests can replace this one function and drive them with recorded
    responses.
    """
    # TODO
    raise NotImplementedError


def post_json(url, payload, headers=None, timeout=TIMEOUT):
    """POST `payload` as a JSON body and return (status_code, parsed_body).

    Send `payload` upward and hand back both halves of what came back: the
    status code and the body, as a two-item tuple.

    Requirements:
      - the body must be sent as JSON, not form-encoded
      - do NOT raise on a 4xx: return the status and whatever body came back,
        because the body is what tells you WHY it failed
      - if the body is not valid JSON, return the raw text as the second
        element instead

    post_json(f"{PLACEHOLDER}/posts", {"title": "hi"})
        -> (201, {"title": "hi", "id": 101})

    Take the second requirement seriously, because it is the opposite of what
    get_json above does and the difference is deliberate. raise_for_status()
    turns a 400 into an exception carrying little more than the number, and
    the number alone tells you the request was your fault without telling you
    which part of it. The body is where the API explains itself — which field
    it objected to, what it expected instead. Throwing that away at the exact
    moment you need it is why this function returns the failure rather than
    raising on it. Callers who want an exception can look at the status and
    raise their own, which is what create_post does next.

    The third requirement exists because a failing server does not always
    answer in JSON. A 500 is quite often an HTML error page from a proxy that
    never reached the application at all. Calling .json() on that raises, so
    catch it and fall back to the raw text — which, being the actual error
    page, is still the most informative thing you have.
    """
    # TODO
    raise NotImplementedError


def create_post(title, body, user_id=1):
    """Create a post on JSONPlaceholder and return the created record.

    Build the payload JSONPlaceholder expects, send it through post_json, and
    interpret the outcome.

    Returns the parsed response dict on 201.
    Raises ValueError with a message containing the status code and the
    response text on any other status.

    This is the layer that decides what counts as failure. post_json is
    deliberately neutral — it reports what happened. create_post has an
    opinion: anything other than a 201 means the record was not created, and
    the caller should not be allowed to carry on as though it were. Putting
    the status code and the response body into the error message means whoever
    reads the traceback gets the API's own explanation for free, instead of
    having to reproduce the call to find out.

    Note JSONPlaceholder fakes the write -- nothing is stored. It still
    returns a genuine 201 with a genuine body, which is all you need.
    """
    # TODO
    raise NotImplementedError


def daily_weather(latitude, longitude, days=7):
    """Fetch a daily forecast from Open-Meteo and reshape it into records.

    The API returns PARALLEL ARRAYS, not records:

        {"daily": {"time": ["2024-01-01", "2024-01-02"],
                   "temperature_2m_max": [4.1, 5.2],
                   "temperature_2m_min": [-1.0, 0.4],
                   "precipitation_sum": [0.0, 2.3]}}

    Read that shape carefully, because it is probably new to you and it is
    common. There is no list of days here. There is one array of dates, one
    array of maximum temperatures, one of minimums, one of rainfall totals —
    and the connection between them is purely positional. Position 0 of every
    array describes the same day; position 1 describes the next one. In SQL
    terms you have been handed the columns without the rows, and it is on you
    to line them up. APIs do this because it compresses well and repeats no
    field names, which is a fine trade for them and an inconvenience for you.

    The inconvenience is real, though, not cosmetic. Nothing downstream can
    use this shape: you cannot sort it, filter it, hand it to pandas, or
    write it to a CSV, because none of those things operate on four
    independent lists that happen to agree about ordering. So the reshape
    below is not tidying up. It is the step that makes every later step
    possible.

    Turn that into one dict per day:

        [{"date": "2024-01-01", "max_c": 4.1, "min_c": -1.0, "precip_mm": 0.0},
         ...]

    Query parameters to send:
        latitude, longitude,
        daily = the three field names above, comma joined,
        timezone = "UTC",
        forecast_days = days

    Use clean_params to build them (pass daily as a LIST and let
    clean_params join it).

    Rules:
      - any of the three value arrays may be shorter than "time" or missing
        entirely; use None for values that aren't there
      - if "daily" or "time" is missing from the response, return []

    That first rule is why you cannot simply index all four arrays at the same
    position and trust it. The dates array is your source of truth for how
    many days there are; the value arrays are not guaranteed to keep up, and
    reaching past the end of a Python list raises IndexError rather than
    quietly giving you nothing. So every read into a value array needs a guard
    that checks the array exists and is long enough, and produces None when it
    is not. Writing that guard once as a tiny helper is much nicer than
    writing the same condition three times.

    One mechanical point that matters for the tests: call get_json as a plain
    module-level name, right where you need it. Two tests work by replacing
    task.get_json with a stand-in that returns a recorded response, and that
    only takes effect if the name is looked up at call time.

    Parallel arrays are a genuinely common API shape and reshaping them is
    the exact thing an interviewer would ask you to do with this endpoint.
    """
    # TODO
    raise NotImplementedError


def fx_series(base, symbols, start_date, end_date):
    """Fetch a date range of FX rates from Frankfurter and flatten it.

    The range goes in the PATH, not the query:
        {FRANKFURTER}/{start_date}..{end_date}?base=USD&symbols=EUR,GBP

    So you build the URL with an f-string and the params dictionary
    separately — the dates are part of the address, while base and symbols are
    ordinary query parameters. The lesson called this the path-parameter
    convention, and a test checks that your URL really does end with the
    range.

    The response looks like:
        {"amount": 1.0, "base": "USD", "start_date": "...",
         "rates": {"2024-01-02": {"EUR": 0.9, "GBP": 0.78},
                   "2024-01-03": {"EUR": 0.91, "GBP": 0.79}}}

    This is the opposite awkward shape from daily_weather, and worth learning
    alongside it. Instead of columns without rows, you have a dictionary whose
    keys are dates, each holding another dictionary whose keys are currency
    codes. The information you want — date, currency, rate — is spread across
    two levels of keys and one value, so flattening means walking the outer
    dictionary, walking each inner one, and emitting a row that carries all
    three pieces explicitly.

    Return a flat, date-sorted list:
        [{"date": "2024-01-02", "currency": "EUR", "rate": 0.9},
         {"date": "2024-01-02", "currency": "GBP", "rate": 0.78},
         {"date": "2024-01-03", "currency": "EUR", "rate": 0.91},
         ...]

    Within a date, currencies are sorted alphabetically.
    `symbols` is a list; send it comma-joined.
    A missing "rates" key gives [].

    Sorting the dates needs no date parsing at all. These are ISO strings —
    YYYY-MM-DD, most significant part first, every part fixed width — so
    ordering them as ordinary text gives you chronological order for free.
    That property is the reason the format is written that way, and sorted()
    on the outer dictionary's keys is the whole implementation.

    As with daily_weather, call get_json as a plain module-level name so the
    fixture-driven test can substitute it.

    Turning a dict-keyed-by-date into rows is the other shape you must be
    able to flatten on sight.
    """
    # TODO
    raise NotImplementedError


def summarize_series(rows):
    """Per-currency summary of fx_series output.

    Take the flat rows fx_series produced and answer the question somebody
    actually asked: for each currency, how many readings were there and what
    did the rate do?

    Return {currency: {"count": n, "min": x, "max": y, "mean": z}} with
    min/max/mean rounded to 4 decimals.

    Rows whose "rate" is None are ignored. A currency with no usable rows
    still appears, with count 0 and None for the three statistics.

    That last sentence is a deliberate design decision rather than an
    inconvenience. A currency you asked about and got nothing usable for is
    information — it belongs in the output, reported honestly as zero
    readings, rather than vanishing and leaving the reader to notice its
    absence. Which also means you cannot build the result only from rows that
    have a rate: collect every currency that appears first, then compute the
    statistics over its non-None rates, and guard the case where there are
    none, because mean is a division and the count can be zero.

    Pure function -- no network. Test it with a hardcoded list.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    print("headers:", build_headers())
    print("\nweather in Berlin:")
    for day in daily_weather(52.52, 13.41, days=3):
        print(" ", day)
    print("\nUSD rates:")
    rows = fx_series("USD", ["EUR", "GBP"], "2024-01-02", "2024-01-05")
    print(json.dumps(summarize_series(rows), indent=2))
