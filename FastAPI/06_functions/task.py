"""Unit 06 task — functions.

Seven functions, and between them they cover every idea the lesson raised: the
mutable default that silently leaks between calls, the two starred parameters
that swallow "however many arguments you were given", the inner function that
remembers a variable after its parent has finished, and the habit of passing a
function around as if it were data.

Three of these are not warm-up exercises — they are things you will write again
later in this course for real. `build_url` is the URL assembly you do in unit
13 against a live API. `retry_call` is the skeleton of the retry helper that
arrives properly in unit 15. `apply_to_field` is the shape of pandas' `.apply()`
and of `sorted(key=...)`. Doing them by hand once means recognising them
instantly the next time.

Write these with ordinary `for` loops and `if` statements. Comprehensions turn
up in unit 07 and would compress away the mechanics you are here to see.

Every docstring shows worked examples in the form `call -> expected result`.
Those lines are the specification — the test file checks exactly those cases, so
read them as the contract rather than as decoration. If the prose and an example
ever seem to disagree, the example wins.

Run:  python -m pytest test_task.py -v
"""


def average(values, default=None):
    """Return the arithmetic mean, or `default` when there is nothing to average.

    Add up the numbers you were given, divide by how many there were, and hand
    the result back. If there is nothing left to average, return whatever the
    caller passed as `default` instead — which is `None` unless they said
    otherwise.

    average([1, 2, 3])          -> 2.0
    average([])                 -> None
    average([], default=0)      -> 0
    average([2])                -> 2.0

    Ignore None entries entirely:
    average([1, None, 3])       -> 2.0
    average([None], default=0)  -> 0

    Why bother: this is the smallest honest example of a function that has to
    decide what to do when there is no data. Real API responses arrive with
    missing fields all the time — a record with no score, a search that matched
    nothing — and `sum(values) / len(values)` on an empty list raises
    ZeroDivisionError, which crashes your whole script over one absent row.
    Dividing by the count of *usable* values rather than the count of values you
    were handed is also the difference between a correct average and one quietly
    dragged toward zero by the gaps.

    Note that `default` is a parameter with a default value of its own, which is
    what lets a caller write either `average(xs)` or `average(xs, default=0)`.
    The value `None` is safe as a default because it cannot be modified in
    place — unlike the list in the next function.
    """
    # TODO
    raise NotImplementedError


def add_tag(tag, tags=None):
    """Append `tag` to `tags` and return the resulting list.

    If the caller handed you a list, add the tag to that list and give the same
    list back. If they did not, build a brand new list containing just the tag.

    add_tag("a")              -> ["a"]
    add_tag("b")              -> ["b"]        <- NOT ["a", "b"]
    add_tag("c", ["x"])       -> ["x", "c"]

    When the caller passes a list, mutate and return THAT list (the tests
    check identity). When they don't, create a fresh one each call.

    Why bother: this function exists for one reason only, which is that you
    write the mutable-default fix with your own hands rather than reading about
    it. Look hard at the second example. Written the obvious way — with
    `tags=[]` in the signature — the second call returns `["a", "b"]`, because
    the `def` line runs exactly once and builds exactly one list, and every call
    that does not supply its own gets a name pointing at that same shared list.
    The tag from the previous call is still sitting in it. Nothing errors; you
    simply get a wrong answer that grows over the lifetime of your program, and
    tracking it down later is miserable.

    So the parameter defaults to `None` — which is immutable, so nothing can
    accumulate on it — and the first thing inside the body checks for that and
    builds a fresh list. Use `is None` for that check rather than testing
    truthiness: a caller who deliberately passes an empty list `[]` should get
    their own list back with the tag appended, not silently swapped for a
    different one. That distinction is exactly what the third example and the
    identity assertion in the tests are protecting.
    """
    # TODO
    raise NotImplementedError


def build_url(base, *path_parts, **query):
    """Assemble a URL from a base, path segments, and query parameters.

    Glue the base address, any path segments, and any query parameters together
    into one well-formed URL string.

    The two starred parameters are what let this function accept a different
    number of arguments on every call. A parameter written with one star,
    `*path_parts`, collects every extra positional argument into a tuple — so
    calling it with three path segments gives you a three-item tuple, and calling
    it with none gives you an empty one. A parameter written with two stars,
    `**query`, collects every extra keyword argument into a dictionary, where
    each key is the name the caller typed and each value is what they set it to.
    You never declare the individual names; the stars do the collecting.

    build_url("https://api.x.com", "users", "torvalds")
        -> "https://api.x.com/users/torvalds"

    build_url("https://api.x.com/", "search", q="python", page=2)
        -> "https://api.x.com/search?q=python&page=2"

    build_url("https://api.x.com", q="a", empty=None)
        -> "https://api.x.com?q=a"

    build_url("https://api.x.com")
        -> "https://api.x.com"

    Rules:
      - exactly one "/" between segments; the base may or may not end in one
      - path parts are converted to strings (ints are legal segments:
        build_url("https://x.com", "users", 42) -> "https://x.com/users/42")
      - query params whose value is None are dropped
      - query params keep the order they were passed in
      - no "?" at all when there are no surviving query params
      - no URL-escaping needed

    Why bother: you will write this for real in unit 13, when you start calling
    live APIs. Building URLs by pasting strings together is where beginners lose
    an hour to a double slash or a stray "?" with nothing after it, and the
    server answers 404 without telling you which part was wrong. Each rule above
    is a bug someone has actually shipped. The None-dropping rule in particular
    matters because it lets you write one call site with every optional filter
    listed, pass `None` for the ones you do not want this time, and have them
    vanish from the URL instead of appearing as `&page=None`.

    The order guarantee is free rather than something you must engineer:
    dictionaries have preserved insertion order since Python 3.7, so `**query`
    hands you the keywords in the sequence the caller typed them.
    """
    # TODO
    raise NotImplementedError


def apply_to_field(records, field, func):
    """Return NEW records with `func` applied to `field`.

    You are given a list of dictionaries, the name of one field, and a function.
    For each record, run that function on the value stored under that field and
    produce a record that is identical except for the transformed value.

    The third argument being a function is the point. `func` is not a piece of
    data you look at; it is something you *call*. Whoever uses this function
    decides what the cleaning actually is — stripping whitespace, uppercasing,
    multiplying by ten — and your code just applies whatever it was handed. Note
    that `str.strip` in the example is passed without parentheses: with
    parentheses you would be calling it and passing on its result, whereas
    without them you are passing the function itself, for this code to call
    later.

    apply_to_field([{"n": "  A "}, {"n": "b"}], "n", str.strip)
        -> [{"n": "A"}, {"n": "b"}]

    Rules:
      - records that lack the field are copied through unchanged
      - records whose field value is None are copied through unchanged
        (calling func on None would usually blow up)
      - the ORIGINAL records must not be modified

    Why bother: passing a function as data is the pattern behind `sorted(key=...)`,
    behind pandas' `.apply()`, and behind FastAPI's dependency injection, which
    you meet in Part 4. Once you have written the pattern once, all three stop
    looking like framework magic and start looking like this function.

    The "must not modify the originals" rule is the other half of the lesson,
    and it is unit 01's names-point-at-objects idea again. If you write
    `record[field] = func(record[field])` you are editing the caller's data
    underneath them, so their variable changes without them asking. Build a copy
    of each dictionary and change the copy. The two skip rules exist because
    real records have holes in them, and `str.strip(None)` raises TypeError —
    one missing value should not take down a run over ten thousand rows.
    """
    # TODO
    raise NotImplementedError


def make_counter():
    """Return a function that returns 1, then 2, then 3, ... on each call.

    This function does not return a number. It returns a *function* — an object
    you store in a variable and then call with parentheses, as many times as you
    like. Each call gives back the next number in sequence, and two counters made
    by two separate calls to `make_counter` count independently of each other.

    c = make_counter()
    c()  -> 1
    c()  -> 2
    d = make_counter()
    d()  -> 1        <- independent from c

    This is a CLOSURE: the inner function keeps a reference to a variable
    from the enclosing function even after that function has returned.

    In other words, you define a small function inside `make_counter`, that
    inner function reads a variable belonging to the outer one, and when
    `make_counter` finishes and hands the inner function out, the variable does
    not disappear — the inner function is still holding on to it. That is why
    each counter has its own private tally that nobody outside can reach or
    corrupt, and why a second counter starts again from one.

    Hint: an inner function that ASSIGNS to a name from the enclosing scope
    needs a keyword to say so -- `global` is not it (that's for module level).
    Look up the other one. Alternatively, sidestep the issue entirely by
    keeping the state in a mutable container, which you can modify without
    rebinding the name.

    Why bother: a counter is the smallest thing that has to remember something
    between calls, so it is the cleanest way to see what a closure buys you. The
    obvious alternative is a module-level variable that the function reads and
    writes, and that is exactly what makes code hard to test — two parts of your
    program end up sharing one hidden number and interfering with each other.
    The same shape underlies rate limiters, ID generators, and the decorators you
    meet later, all of which are functions that wrap state up where only they can
    touch it.
    """
    # TODO
    raise NotImplementedError


def retry_call(func, attempts=3, on_error=None):
    """Call `func()` repeatedly until it returns a non-None value.

    Return the first non-None result. If every attempt yields None, return
    `on_error`.

    The first argument is a function, passed in without parentheses, and your
    job is to decide *when* and *how often* it runs. That inversion — the caller
    supplies the work, you supply the control — is the same one you already met
    in unit 05, where `collect_pages(fetch_page)` took a fetching function so the
    paging logic never needed to know how a page actually arrives.

    Requirements:
      - call func() at most `attempts` times
      - stop the instant a non-None value comes back
      - attempts <= 0 means don't call func at all; return on_error

    retry_call(lambda: 5)                    -> 5      (one call)
    retry_call(lambda: None)                 -> None   (three calls)
    retry_call(lambda: None, on_error="!")   -> "!"

    No exception handling here -- unit 08 adds that. This is about the
    "take a function as an argument and control when it runs" mechanic,
    which is the core of every retry helper you will ever write.

    Why bother: networks fail intermittently, and the difference between a
    script that dies on one dropped packet and one that finishes is a loop
    roughly this shape. You write it properly, with backoff and real exception
    handling, in unit 15; here you build the skeleton so that version has
    nothing surprising in it. Stopping the moment a good value appears is what
    keeps the common case fast, and honouring `attempts <= 0` is what stops a
    computed-somewhere-else zero from turning into an infinite loop.

    One contrast worth holding on to, because it is easy to misread later. Here,
    `None` counts as a failure and triggers another attempt. In unit 08 you meet
    `first_successful`, which treats `None` as a perfectly good result and only
    retries when the call raises an exception. Same general idea, opposite
    treatment of `None` — so when you compare the two, check what each one
    considers a failure before assuming they behave alike.
    """
    # TODO
    raise NotImplementedError


def compose(*funcs):
    """Return a function that applies each of `funcs` LEFT TO RIGHT.

    Take however many functions you were given — the single star collects them
    all into a tuple — and return one new function that runs them in order,
    feeding the output of each into the next.

    pipeline = compose(str.strip, str.lower)
    pipeline("  ABC ")  -> "abc"

    compose()("x")  -> "x"     <- no functions: identity

    Note "left to right" is the pipeline reading order, which is the opposite
    of the mathematical convention f(g(x)). Pipeline order is what you want
    for data cleaning.

    Why bother: cleaning a field is almost never one operation. It is strip the
    whitespace, then lowercase, then cut it to a maximum length. Written inline
    that becomes a nest of calls read inside-out; built with `compose` it becomes
    a named pipeline you can hand to `apply_to_field` above, reuse on another
    field, and describe out loud in one sentence. This function both takes
    functions as arguments and returns a function, so it is where the two ideas
    of this unit meet.

    The no-arguments case is worth getting right rather than special-casing: a
    pipeline with no steps should hand the value straight back untouched, and if
    you loop over an empty tuple that falls out on its own.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    print(build_url("https://api.github.com", "users", "torvalds"))
    print(build_url("https://api.github.com/", "search", q="python", page=2))
    counter = make_counter()
    print(counter(), counter(), counter())
