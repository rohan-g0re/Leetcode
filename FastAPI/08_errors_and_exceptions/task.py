"""Unit 08 task — errors and exceptions.

Seven functions, and between them they cover the whole of what the lesson
taught: attempting an operation instead of checking whether it will work,
catching only the failures you have an actual plan for, collecting the ones
you cannot fix rather than hiding them, and raising errors of your own when
somebody hands your function something it cannot use.

Two of these are old friends. `to_float` is unit 01's `coerce_number` written
with the tool you were missing at the time, and it will come out to two lines
instead of twelve. `safe_field` is unit 04's `deep_get` written the other way
round — catching the error instead of checking for it. Writing the same
function twice, once each way, is the fastest route to being able to say out
loud why you chose the style you chose.

Every function's docstring shows worked examples in the form
`call -> expected result`. Those lines are the specification — the tests check
exactly those cases, so read them as the contract rather than as decoration.
If the prose and an example ever seem to disagree, the example wins.

Run:  python -m pytest test_task.py -v
"""


class ValidationError(Exception):
    """Raised when input data fails a check we care about.

    This is your own exception type, and defining one takes exactly the two
    lines you see here: a class that inherits from `Exception`, and a
    docstring saying what it means. Because it is a kind of `Exception`, it
    behaves like every built-in error you have already met — it can be raised,
    caught, and printed the same way.

    The reason to have your own type at all is that it lets a caller tell
    *your* complaints apart from Python's accidents. Someone catching
    `ValidationError` gets only the failures you deliberately signalled, and
    not, say, a typo elsewhere that produced a `KeyError`. `validate_page_size`
    below is where you raise it.
    """


def to_float(value, default=None):
    """Convert anything to a float, returning `default` when it can't be done.

    You are handed some value that is supposed to represent a number and may
    or may not actually be one. Try to turn it into a float. If that works,
    hand back the float. If it doesn't work for any reason at all, hand back
    `default` instead of letting the failure escape.

    This is unit 01's coerce_number, done properly.

    to_float("3.5")   -> 3.5
    to_float(" 7 ")   -> 7.0
    to_float("abc")   -> None
    to_float(None)    -> None
    to_float("1e3")   -> 1000.0      <- float() handles this; your manual
                                        version in unit 01 did not
    to_float("nope", default=0.0) -> 0.0

    Booleans still convert (float(True) is 1.0) and that is fine here --
    do not special-case them.

    Use try/except. Two lines of body.

    Why bother: this is the single clearest payoff in the whole unit. In
    unit 01 you wrote this by inspecting the value's type by hand, deciding
    whether it looked convertible, and only then converting — about a dozen
    fiddly lines, and it still got `"1e3"` wrong, because a human eye doesn't
    naturally read that as scientific notation for one thousand. Handing the
    job to `float()` and catching the failure gets you two lines and correct
    behaviour on every case, including the ones you would never have thought
    to check for.

    The thing to understand before you write it is *which* failures you are
    catching, because `float()` has two different ways of refusing. It raises
    `ValueError` when the thing you gave it is the right kind of object but
    the wrong content — a string, but a string like `"abc"` or `""` that
    doesn't spell out a number. It raises `TypeError` when the object isn't
    the sort of thing that could ever be converted, such as `None`, a list, or
    a dict. Those are genuinely different diagnoses, and Python is right to
    keep them apart.

    You want one handler for both, and that is not laziness — it is because
    from your caller's point of view the two mean exactly the same thing:
    "that wasn't a number, use the fallback." You are still catching narrowly,
    naming the two specific types you anticipated; a typo inside the block
    would still crash loudly, which is what you want. `except (A, B):` with
    the parentheses is how you name two types in one handler.
    """
    # TODO
    raise NotImplementedError


def safe_field(record, *keys, default=None):
    """deep_get from unit 04, implemented with try/except instead of checks.

    You get a nested dictionary and a sequence of keys naming a path down
    into it. Walk that path one key at a time and return whatever you find at
    the end. If the path breaks anywhere along the way, return `default`.

    The `*keys` in the signature means the caller passes the path as ordinary
    separate arguments — `safe_field(record, "user", "address", "city")` —
    and inside the function `keys` arrives as a tuple of those values, which
    you can loop over. A caller who passes no keys at all gets the record
    back untouched, since a zero-step walk ends where it started.

    safe_field({"a": {"b": 1}}, "a", "b")     -> 1
    safe_field({"a": None}, "a", "b")         -> None
    safe_field({}, "x", default=0)            -> 0

    Catch exactly the exception types that indexing can raise here, not a
    blanket Exception. Think about which ones can actually occur:
      - the key isn't there
      - the current value is None or a number, so it can't be indexed at all

    Why bother: this is unit 04's `deep_get` again, but written the other way
    round. There you checked at every step whether it was safe to go deeper;
    here you simply go, and catch the complaint if there isn't a next step.
    The result is shorter and, more usefully, it copes with breakages you
    didn't enumerate. Having now written the same function in both styles,
    you can answer the interview question "when would you check first and
    when would you just try it?" from experience rather than from a slogan.

    Work out for yourself which types belong in the handler — that is the
    exercise, and it is worth ten minutes of thinking. To give you the
    footing: `KeyError` is what a dictionary raises when you ask it for a key
    it does not have, so `{}["x"]` raises it. `TypeError` is what you get when
    the thing you are indexing is not indexable by a key at all — `None["b"]`
    and `1["b"]` both raise it, because neither `None` nor an integer supports
    that operation. `IndexError` is the list version, raised when you ask for
    position 5 of a three-item list. Decide which of those your walk can
    genuinely produce, given the examples above, and name only those.
    """
    # TODO
    raise NotImplementedError


def parse_records(raw_records):
    """Convert raw records into clean ones, collecting failures instead of dying.

    You are given a list of dictionaries straight off an API, some of which
    are fine and some of which are not. Walk the list once, clean up the ones
    you can, and keep a note of the ones you can't along with the reason.
    Nothing here is allowed to crash and nothing is allowed to vanish
    silently.

    Each raw record should have "id" (any value) and "amount" (convertible to
    float). Return a tuple (good, failures) where:

      good     = [{"id": ..., "amount": <float>}, ...]
      failures = [{"id": <id or None>, "error": "<message>"}, ...]

    A record fails when:
      - it has no "id" key            -> error message "missing id"
      - it has no "amount" key        -> error message "missing amount"
      - "amount" won't convert        -> error message "bad amount"

    Check in that order, and report only the FIRST problem per record.

    parse_records([
        {"id": 1, "amount": "10.5"},
        {"id": 2},
        {"amount": 5},
        {"id": 4, "amount": "abc"},
    ])
    -> ([{"id": 1, "amount": 10.5}],
        [{"id": 2, "error": "missing amount"},
         {"id": None, "error": "missing id"},
         {"id": 4, "error": "bad amount"}])

    Order in both lists follows the input order.

    This shape -- (good, failures) -- is worth remembering. Returning the
    failures instead of printing them lets the caller decide whether to
    warn, abort, or ignore.

    Why bother: this is the honest middle ground between the two bad options.
    Crashing on the first malformed record throws away the four hundred good
    ones behind it. Silently skipping the bad ones — the `except: pass` the
    lesson warned about — leaves you quietly reporting on less data than you
    think you have, with nothing to tell you so. Collecting the failures gets
    you both: every record that could be cleaned, and an exact account of
    every one that couldn't and why.

    The reason to *return* the failures rather than print them is that
    printing decides the response on the caller's behalf. A function that
    hands back both lists lets one caller warn, another abort, and a third
    ignore, without any of them editing this function. And it gives you the
    sentence that makes you sound like someone who has handled real data:
    "I processed 487 of 500 records; the 13 that failed were missing an
    amount field, and here they are."

    Note the checks are ordered, and only the first problem in a record is
    reported — a record missing both "id" and "amount" is reported as
    "missing id" and nothing else. That is why the fourth test case exists.

    You have already written the amount-conversion half of this. Reach for
    `to_float` rather than writing a second try/except here; a bad amount is
    exactly the case where it returns its default.
    """
    # TODO
    raise NotImplementedError


def validate_page_size(size):
    """Return the size if valid, otherwise raise ValidationError.

    This is the first function in the course that refuses to do its job. If
    `size` is acceptable, hand it straight back unchanged. If it isn't, raise
    the `ValidationError` defined at the top of this file rather than
    returning some signal value the caller might ignore.

    Valid: an int (not a bool, not a float, not a numeric string) between
    1 and 100 inclusive.

    validate_page_size(50)     -> 50
    validate_page_size(0)      -> raises ValidationError
    validate_page_size(101)    -> raises ValidationError
    validate_page_size("50")   -> raises ValidationError
    validate_page_size(True)   -> raises ValidationError

    The message must mention the offending value, so whoever reads the
    traceback does not have to guess. The tests check that str(exc) contains
    str(size).

    Why bother: fail at the door, not in the basement. A page size of 5000
    that you accept here doesn't hurt until much later — the request goes
    out, the server rejects it or truncates it, and what you eventually see
    is a confusing symptom two hundred lines away from the mistake. Refusing
    it at the boundary of your own function means the traceback points
    directly at the bad value, and that is the difference between a
    thirty-second fix and an afternoon.

    That is also why the message has to contain the offending value. "Invalid
    page size" tells the reader nothing they didn't already know; "page_size
    must be an int in 1..100, got 5000" tells them exactly what to change.

    The genuinely hard part is `True`. Python builds its boolean type on top
    of its integer type — `bool` is a sub-type of `int`, which is the formal
    version of the fact you met in unit 01, that `True` behaves as `1` in
    arithmetic. The consequence is that `isinstance(True, int)` evaluates to
    `True`, so the obvious "is this an integer?" check waves booleans
    straight through, and `True` then passes the 1-to-100 range check too,
    because it is 1. You need a separate check for `bool`, and it has to come
    before the `int` check, not after.
    """
    # TODO
    raise NotImplementedError


def first_successful(funcs, default=None):
    """Call each function in turn; return the first result that doesn't raise.

    You are handed a list of zero-argument functions, in priority order. Call
    the first one. If it returns anything at all, that is your answer and you
    stop — you must not call the rest. If it raises, move down the list and
    try the next one.

    If a function raises ANY Exception, move on to the next one. If all of
    them raise (or the list is empty), return `default`.

    first_successful([lambda: 1/0, lambda: "ok"])          -> "ok"
    first_successful([lambda: 1/0], default="fallback")    -> "fallback"
    first_successful([lambda: None])                       -> None
      (None is a legitimate RESULT here, not a failure -- unlike unit 06's
       retry_call. Read that difference carefully.)

    This is the "try several sources, use whichever works" pattern: hit the
    cache, fall back to the API, fall back to a default.

    Read that third example again, because it is the one people get wrong.
    In unit 06 you wrote `retry_call`, which treats a returned `None` as a
    failure and keeps trying. This function does not. Here, only a *raised
    exception* counts as failure; a function that returns `None` has
    succeeded, and `None` is the answer you return. The two functions look
    almost identical on the page and differ on exactly this point, and the
    tests check it. The reason for the difference is what each one models:
    `retry_call` retries a flaky operation where `None` means "no result
    yet", whereas here `None` may be the perfectly correct contents of a
    cache entry, and re-fetching it from a slower source would be wrong.

    Why bother: this is how real systems get their data. Check the local
    cache; if that misses, call the API; if that is down, use a hardcoded
    default. You want the fastest source that works, and you want the whole
    thing to degrade quietly instead of collapsing when one layer is
    unavailable.

    This is also the one place in this unit where a broad handler is the
    right call rather than a lazy one — see the hints for why, once you have
    tried it.
    """
    # TODO
    raise NotImplementedError


def describe_exception(func):
    """Call func() and return a string describing what happened.

    Run the function you were given. Either it worked, in which case say so,
    or it raised something, in which case describe what it raised in one
    readable line. Whatever happens, this function itself must not raise —
    the point is to turn a failure into a piece of text you can log or show
    to a person.

    On success:  "ok"
    On failure:  "<ExceptionClassName>: <message>"

    describe_exception(lambda: 1)        -> "ok"
    describe_exception(lambda: 1/0)      -> "ZeroDivisionError: division by zero"
    describe_exception(lambda: int("x")) -> "ValueError: invalid literal for int() with base 10: 'x'"

    Hint: an exception object's class has a __name__, and str() of the
    exception gives its message.

    Unpacking that hint, since it is the whole exercise. Catching with
    `except Exception as exc:` gives you the exception object itself in a
    variable named `exc`. That object carries the two things the lesson said
    every exception carries. `type(exc)` is its class — the type — and
    `type(exc).__name__` is that class's name as an ordinary string, so for a
    division by zero you get `"ZeroDivisionError"`. Meanwhile `str(exc)` is
    the message alone, with no type name attached: `"division by zero"`. Join
    them with a colon and a space and you have the format above.

    One surprise waits in the tests. `str()` of a `KeyError` is the missing
    key *including its quote marks*, so a `KeyError` for the key `x` yields
    `'x'` rather than `x`, and the expected output is `"KeyError: 'x'"`. That
    is not a mistake in the test — `KeyError` really does report its message
    that way, so that a missing key of `""` is still visible. It catches
    everyone once; now it has caught you here instead of somewhere expensive.

    Why bother: this is the shape of every log line you will ever write about
    a failure. When a batch job skips a record, "row 412 failed" is useless
    and the full traceback is too much; one line naming the type and the
    message is exactly the right amount. It is also the string you would put
    in the `"error"` field of `parse_records`' failure entries once those
    failures come from arbitrary code rather than from checks you wrote.
    """
    # TODO
    raise NotImplementedError


def divide_all(pairs):
    """Divide each (a, b) pair, using None where the division is impossible.

    You get a list of two-item tuples. For each one, divide the first by the
    second and put the answer in the output list. When a particular division
    cannot be done, put `None` in that position instead. The output list is
    always the same length as the input, so position 2 of the result still
    corresponds to pair 2 of the input.

    divide_all([(10, 2), (1, 0), (9, 3)])  -> [5.0, None, 3.0]
    divide_all([("a", 2)])                 -> [None]

    Catch only what can actually go wrong: dividing by zero, and dividing
    things that aren't numbers.

    Those two failures have two different names. Dividing by zero raises
    `ZeroDivisionError`, because the arithmetic itself has no answer.
    Dividing a string by a number raises `TypeError`, because `/` is not an
    operation those two kinds of thing support together. Name both and
    nothing else — a broad handler here would also swallow, say, a tuple with
    the wrong number of items, which is a bug you would rather hear about.

    Why bother: this is the per-item version of everything above. Whenever
    you compute a rate — conversions per visit, errors per request, revenue
    per customer — some denominator will eventually be zero, and one such row
    should not destroy the other nine hundred. Keeping a `None` in place
    rather than dropping the row is the detail that matters, because it keeps
    the result lined up with the input and lets whoever reads it see that the
    value is missing rather than quietly absent.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    print(to_float("1e3"))
    print(parse_records([{"id": 1, "amount": "10.5"}, {"id": 2}]))
    print(describe_exception(lambda: 1 / 0))
