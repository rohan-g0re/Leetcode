"""Unit 01 task — values, types, and variables.

This is your first Python task, and every one of the eight functions below is a
small piece of real work you will do again and again once you are handling live
API data. None of them is a puzzle. Each one exists because some genuine thing
goes wrong when you don't have it.

How to work through this file. Each function is a stub: it has a name, a
docstring explaining what it must do, a `# TODO` comment marking where your code
goes, and a line saying `raise NotImplementedError`. That last line is a
placeholder meaning "nobody has written this yet" — delete it and put your own
code in its place. Work top to bottom; they get slightly harder as you go.

To check your work, run the tests. A test is just another Python file that calls
your functions with known inputs and complains if the answers are wrong. From a
terminal, in this folder:

Run the tests:      python -m pytest test_task.py -v
Run just one:       python -m pytest test_task.py::test_safe_divide -v

One rule that will save you a confusing half hour. Every function here must
*return* its answer rather than print it. Returning hands the value back to
whoever called the function, so it can be used; printing just paints text on
your screen and hands back nothing at all. If you print instead of return, the
caller receives `None`, your tests fail, and the output on screen looks
completely correct — which is exactly why this is the most common mistake
beginners make. Nothing here should print, ask for input, or touch the network:
give the same function the same input and it must always give the same answer
back.
"""


def describe_type(value) -> str:
    """Take any value and hand back the name of its type, as lowercase text.

    So given the number 5 you return the string "int", and given None you return
    the string "nonetype". You are not returning the type itself here — you are
    returning its *name*, written out as ordinary text.

    describe_type(5)      -> "int"
    describe_type(5.0)    -> "float"
    describe_type("x")    -> "str"
    describe_type(True)   -> "bool"
    describe_type(None)   -> "nonetype"

    Why bother writing this? Because the first question you ask about any piece
    of data you did not create yourself is "what kind of thing is this?", and
    when an API response surprises you, the fastest way to find out is to loop
    over the fields and print the type of each one. A service that sends you
    {"population": "1400000"} — a number written as text — looks identical to
    one that sends a real number until you check. This function is the tool you
    reach for at that moment.

    Where to start. `type(value)` gives you back a *type object*, which is
    Python's internal description of a kind of thing; printing one shows
    something like `<class 'int'>`. That object carries its own name inside it as
    an attribute. To find out what that attribute is called, open the
    interactive Python prompt and run `dir(type(5))` — `dir` lists everything
    attached to a value. The one you want begins and ends with two underscores.
    Once you have the name, remember the examples above are all lowercase.
    """
    # TODO

    return type(value).__name__.lower()

    raise NotImplementedError


def safe_divide(numerator, denominator):
    """Divide the first number by the second, but never crash on a zero divisor.

    Normally you would just write `numerator / denominator`. The problem is that
    dividing by zero in Python is not merely wrong, it raises an error and stops
    your whole program dead. So this function does the division when it can, and
    returns None — Python's word for "there is no answer here" — when the
    denominator is zero.

    safe_divide(10, 4)  -> 2.5
    safe_divide(10, 0)  -> None
    safe_divide(0, 5)   -> 0.0

    Why this is worth writing. Every average you ever compute is a total divided
    by a count, and sooner or later a count is zero — a category with no records
    in it, a filter that matched nothing, a day with no traffic. Without this
    guard, one empty group at record four hundred kills a script that has
    already done all the hard work. With it, you get None for that group and
    everything else still comes through. This is probably the single most
    frequently repeated defensive line in the whole course.

    Where to start. One `if` that checks the denominator before you divide, and
    the division itself afterwards. Note that `/` in Python always produces a
    float — a number with a decimal point — even when the division comes out
    even, which is why the third example is 0.0 rather than 0.
    """
    # TODO

    if(denominator == 0):
        return None
    else: return numerator / denominator

    raise NotImplementedError


def is_missing(value):
    """Decide whether a value genuinely means "no data", and answer True or False.

    Only three things count as missing: None, the empty string "", and a string
    containing nothing but blank space such as "   " or a tab. Everything else
    counts as present, and that emphatically includes 0, 0.0, False, an empty
    list [], and the text "0" — those are all real values that someone
    deliberately sent you.

    Treat as missing:  None, "" (empty string), and "   " (whitespace only).
    Treat as PRESENT:  0, 0.0, False, [] and "0".

    Why this function exists, and it is the most important idea in this file.
    Python has a shortcut where you can use any value as a yes-or-no test, and
    it decides that 0, empty text, and empty lists all count as "no". That
    shortcut is convenient and it is also a trap. An API that sends you
    {"score": 0} is telling you something true: this thing scored zero. An API
    that sends {"score": null} is telling you it has no idea. Those are
    completely different facts, and the shortcut collapses them into the same
    answer. The bug never shows up in your test data, because your test data has
    non-zero scores; it shows up on the one real record where somebody scored
    nothing. This function forces you to draw the line in the right place.

    Where to start. Handle None before you do anything else, because if you call
    a text method on None, Python raises an error and stops. After that, ask
    whether the value is a string at all — `isinstance(value, str)` answers that
    — and only then look at its contents. Strings have a built-in method that
    trims blank space off both ends; if trimming leaves you with nothing, the
    string was blank. Everything that isn't None and isn't a blank string is
    present. One last detail: the tests check your answer with `is True` and
    `is False`, which demands the actual values True and False rather than
    something that merely behaves like them, so return them explicitly.
    """
    # TODO

    if value: return True
    else: return False

    raise NotImplementedError


def coerce_number(value):
    """Turn a value into a float if it plausibly is a number, and None if it isn't.

    "Coerce" is the word programmers use for forcing a value from one type into
    another. Here you are given whatever an API happened to send — a number,
    some text, a true/false flag, nothing at all — and you must hand back a
    float when the value really does represent a number, and None when it
    doesn't. Notice that you never crash and you never guess: an unusable value
    becomes None, which the caller can then skip.

    coerce_number(42)        -> 42.0
    coerce_number("42")      -> 42.0
    coerce_number("3.5")     -> 3.5
    coerce_number("  7 ")    -> 7.0
    coerce_number("abc")     -> None
    coerce_number(None)      -> None
    coerce_number("")        -> None
    coerce_number(True)      -> None     <- booleans are NOT numeric data here

    Why this is the function that earns its keep. Real services are wildly
    inconsistent about types, and the same field can arrive as 42 from one
    endpoint and "42" from another, sometimes with stray spaces around it
    because a human typed it into a spreadsheet years ago. If you don't clean
    that up on the way in, Python will silently treat your numbers as text and
    "glue" them together instead of adding them, and you will get a wrong answer
    that looks perfectly reasonable. Cleaning every incoming value through one
    function like this is how you stop that happening. True is excluded on
    purpose: a true/false flag is not a measurement, and letting it slide
    through as 1.0 would quietly corrupt any total you computed.

    Where to start. The obvious move is to call `float(value)` and see what
    happens, but that raises an error and halts your program on bad text or on
    None. There is a proper way to catch an error rather than avoid it — it's
    called try/except, and it's unit 08 — but you haven't met it yet, and doing
    this the hard way once is exactly what makes unit 08 feel like a relief. So
    instead, inspect the type up front and decide what to do for each case,
    using `isinstance(value, str)` and friends.

    Two things that will catch you out. First, `isinstance(True, int)` is True,
    because Python builds its true/false type on top of its integer type; so if
    you check for int before you check for bool, True slips through as 1.0.
    Check bool first. Second, for text: strip the spaces off, and if nothing is
    left it isn't a number. Strings do have a method that reports whether they
    are a run of digits, but it answers False for "3.5" and for "-7", both of
    which the examples require you to accept. So that method alone is not
    enough — look at the full list of inputs the tests use, and work out what
    shapes of text you actually need to allow.
    """
    # TODO

    if(type(value) is int): return float(value)
    else: return None

    raise NotImplementedError


def bucket(n, size):
    """Work out which group of width `size` the number n belongs to.

    Imagine laying out numbered bins side by side, each one `size` wide. The
    first bin covers 0 up to but not including `size`, the next covers `size` up
    to twice `size`, and so on. Given n, tell me which bin it lands in, counting
    from 0. With size 10, the numbers 0 through 9 all land in bin 0, and 37
    lands in bin 3.

    bucket(0, 10)    -> 0
    bucket(7, 10)    -> 0
    bucket(10, 10)   -> 1
    bucket(37, 10)   -> 3
    bucket(37, 25)   -> 1

    If size is 0 or negative, return None.

    Why you want this. Grouping continuous numbers into bands is how you turn a
    pile of raw values into something you can actually say a sentence about.
    Ages become decades, timestamps become hours of the day, scores become
    grade bands. It's the same move as a GROUP BY over a computed column in SQL,
    and it's the step that turns "here are nine hundred numbers" into "most of
    the traffic arrives between 9am and 11am."

    Where to start. The whole calculation is one division — but not the ordinary
    kind, because you want a whole-numbered bin, not 3.7. Python has a second
    division operator that divides and then rounds down; it's two slashes rather
    than one. And guard the bad `size` first: a size of zero would divide by
    zero, and a negative size is meaningless, so both should give you None
    before any arithmetic happens.
    """
    # TODO

    return (n % size)

    raise NotImplementedError


def percent_change(old, new):
    """Say how much a value grew or shrank, as a percentage, to two decimals.

    Given the old value and the new one, report the change relative to where it
    started. Going from 100 to 150 is a 50 percent rise, so you return 50.0.
    Going the other way gives you a negative number. Round the answer to two
    decimal places.

    percent_change(100, 150)  -> 50.0
    percent_change(100, 50)   -> -50.0
    percent_change(80, 80)    -> 0.0
    percent_change(0, 10)     -> None     <- undefined; cannot divide by zero
    percent_change(50, 0)     -> -100.0

    Formula: (new - old) / old * 100

    Why it matters. When an interviewer hands you two snapshots of an API and
    asks what changed, a percentage is the answer they actually want — raw
    differences mean nothing without knowing how big the thing was to begin
    with. The interesting case is the fourth example. Growth from zero has no
    percentage: any increase from nothing is infinitely large, which is why the
    honest answer is None rather than a made-up number. Recognising that a
    metric is undefined, and saying so instead of printing something confident
    and wrong, is a real part of doing this job well.

    Where to start. The formula is given to you, so the work is in the order of
    operations. Check for the zero starting value before you divide by it, then
    apply the formula, then round. Python's `round` takes the number first and
    the number of decimal places second.
    """
    # TODO

    change = new - old

    if(change == 0): return None
    else:
        return (change // old) * 100 

    raise NotImplementedError


def clamp(value, low, high):
    """Pull a value back inside an allowed range, and return the result.

    To "clamp" is to hold something within limits. If the value already sits
    between low and high, hand it straight back unchanged. If it's below low,
    return low; if it's above high, return high. Both ends count as allowed, so
    a value exactly equal to low or high passes through untouched.

    clamp(5, 1, 10)    -> 5
    clamp(-3, 1, 10)   -> 1
    clamp(99, 1, 10)   -> 10

    Why you'll reach for this constantly. The moment you start calling real APIs
    you will be passing them page sizes, and every service has a ceiling — ask
    GitHub for 5000 results per page and the request is rejected. Writing
    clamp(user_requested_page_size, 1, 100) means a caller can ask for anything
    at all and you still send a legal request. It's also how you keep a
    percentage inside 0 to 100, or a retry delay inside sensible bounds. Any
    time a number arrives from outside your control, clamping is cheaper than
    validating and apologising.

    Where to start. Write this as ONE expression built from two of Python's
    built-in tools — no `if` statements. The two tools are `min`, which returns
    the smaller of the arguments you give it, and `max`, which returns the
    larger. Try nesting one inside the other and check both directions against
    the examples above; convince yourself why the nesting handles the too-low
    case and the too-high case at the same time.
    """
    # TODO

    return min(max(value, low), high)
    raise NotImplementedError


def format_summary(name, count, average):
    """Build one line of readable text summarising a name, a count, and an average.

    You are given three pieces of data and must assemble them into a single
    string in exactly the shape shown below — the punctuation and spacing are
    part of the answer, so copy them precisely.

    format_summary("torvalds", 8, 1234.5678)
        -> "torvalds: 8 items, avg 1234.57"

    format_summary("empty", 0, None)
        -> "empty: 0 items, avg n/a"

    Rules:
      - average is shown to exactly 2 decimal places
      - when average is None, show the literal text n/a
    Use an f-string.

    Why this is the right function to finish on. Everything above turns messy
    data into clean data; this turns clean data into an answer a human can read.
    In an interview, the last thing you do after fetching and cleaning is say
    something out loud about what you found, and a tidy formatted line does that
    far better than a dumped raw number. The None case matters just as much:
    "avg n/a" honestly reports that there was nothing to average, whereas
    printing 0.00 would be a quiet lie.

    Where to start. An f-string is Python's way of dropping values into text.
    You put the letter f immediately before the opening quote, and anything you
    write inside curly braces gets evaluated and inserted:
    f"{name} has {count}". To control how a number is displayed, add a colon and
    a format code inside the braces — `.2f` means "two decimal places". The
    None case needs a decision before the formatting, since you cannot ask for
    two decimal places of nothing; the cleanest route is to work out the average
    text first, store it in a variable, and then build one f-string from it.
    """
    # TODO

    if(average is None): return f"{name}: {count} items, avg n/a"
    else: return f"{name}: {count} items, avg {average:.2f}"

    raise NotImplementedError


if __name__ == "__main__":
    # Running this file directly (python task.py) executes this block, but
    # importing it from the tests does not. Use it to poke at your own code.
    print(describe_type(5))
    print(safe_divide(10, 0))
    print(format_summary("demo", 3, 1.005))
