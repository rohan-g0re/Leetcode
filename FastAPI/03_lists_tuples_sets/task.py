"""Unit 03 task — lists, tuples, and sets.

Nine small functions, each one a thing you will genuinely do to a list of
records that came back from an API. Work through them in order; they get
slightly harder as you go, and the last one is a classic interview question.

Write these with ordinary `for` loops. Python has a shorter way of expressing
most of them, called a comprehension, but that arrives in unit 07 and using it
now would hide the very mechanics you are here to see. Loops first, brevity
later.

Every function's docstring shows worked examples in the form
`call -> expected result`. Those lines are the specification — the tests check
exactly those cases, so read them as the contract rather than as decoration.
If the prose and an example ever seem to disagree, the example wins.

Run:  python -m pytest test_task.py -v
"""


def dedupe_preserving_order(items):
    """Remove duplicates while keeping first-seen order.

    Given a list that may contain the same value more than once, hand back a
    new list holding each distinct value exactly once, in the order those
    values first appeared.

    dedupe_preserving_order([3, 1, 3, 2, 1])  -> [3, 1, 2]
    dedupe_preserving_order([])               -> []

    list(set(items)) would lose the order. Do it properly.

    Why bother: paginated APIs hand you the same record twice all the time, and
    duplicated rows quietly inflate every count and average you compute
    afterwards. You could dedupe with `set(items)`, but a set has no order, so
    your "top ten most recent" would come back scrambled differently on each
    run — which makes output impossible to eyeball and tests impossible to
    write. You want the deduplication a set gives you *and* the order a list
    gives you, so use both together: one to remember what you have already
    seen, one to hold the answer. Also, do not modify the list you were handed;
    build and return a new one.
    """
    # TODO
    raise NotImplementedError


def chunk(items, size):
    """Split a list into consecutive chunks of at most `size` items.

    Walk the list front to back and cut it into pieces of `size` items each.
    The last piece is allowed to be short, because the list rarely divides
    evenly. Return a list of those pieces.

    You need this to send IDs to an API that accepts at most N per request --
    an extremely common real constraint.

    chunk([1,2,3,4,5], 2)  -> [[1,2], [3,4], [5]]
    chunk([1,2,3], 5)      -> [[1,2,3]]
    chunk([], 3)           -> []
    chunk([1,2,3], 0)      -> []      (invalid size: return empty, don't crash)

    Why bother: almost every real API caps how much you may ask for at once —
    a hundred IDs per lookup, five hundred rows per page. If you have four
    thousand IDs, you cannot send them in one request; you have to slice them
    into batches and loop. That slicing is this function, and once you have it
    you can point it at any endpoint with any limit.

    Note the `size` of 0 case. A caller could easily compute that size from
    another variable and get zero by accident, and if you looped on it you
    would loop forever. Refusing an impossible batch size up front is cheaper
    than debugging a hang later.

    Hint: range() takes a step argument, and slicing never goes out of bounds.
    """
    # TODO
    raise NotImplementedError


def flatten(nested):
    """Flatten one level of nesting.

    You are given a list whose items are themselves lists. Return a single
    flat list containing every inner item, in order. One level only — you are
    not digging recursively into lists inside lists inside lists.

    flatten([[1,2],[3],[]])   -> [1,2,3]
    flatten([])               -> []

    You get exactly this shape when you collect several pages of results and
    end up with a list of pages, each of which is a list of records.

    Why bother: when you fetch page one, page two, page three and collect each
    response, what you are holding is a list of pages, not a list of records.
    Nothing downstream wants that — `len()` tells you how many pages you
    fetched rather than how many records you got, and looping gives you page
    objects rather than rows. Flattening once, right after collection, means
    the rest of your program deals with a simple list of records.

    The tool that does most of the work here is a list method that adds every
    item of another collection rather than adding that collection as one item.
    Unit 03's lesson contrasts it with its near-twin; picking the right one of
    the two is the whole exercise.
    """
    # TODO
    raise NotImplementedError


def min_max(numbers):
    """Return (minimum, maximum) as a tuple, or None for an empty input.

    Find the smallest and largest numbers and give both back at once, packaged
    as a two-item tuple. If there are no numbers at all, return None, because
    there is no honest answer to "what is the smallest of nothing."

    min_max([3, 1, 4])  -> (1, 4)
    min_max([5])        -> (5, 5)
    min_max([])         -> None

    Why bother: this is the smallest possible example of returning two values
    from one function, which Python does by building a tuple — there is no
    separate multiple-return feature. The caller then writes
    `low, high = min_max(scores)` and gets both back in one line. Once you have
    seen it here, every function you meet that returns "a pair" or "a triple"
    stops looking mysterious.

    The empty case is the real lesson though. Python's built-in min() and max()
    raise an error on an empty list, and an empty list is exactly what an API
    hands you when a search matches nothing. Deciding what your function does
    with no data, before it happens, is most of what makes code survive
    contact with real responses.
    """
    # TODO
    raise NotImplementedError


def compare_id_sets(left, right):
    """Compare two collections of IDs and report the three-way split.

    Given two collections of IDs, work out which IDs appear only in the first,
    which appear only in the second, and which appear in both.

    Return a tuple (only_left, only_right, in_both) where each element is a
    SORTED LIST (not a set) so the result is deterministic and printable.

    compare_id_sets([1,2,3], [2,3,4])  -> ([1], [4], [2,3])
    compare_id_sets([], [1])           -> ([], [1], [])
    compare_id_sets([1,1,2], [2])      -> ([1], [], [2])

    This is the reconciliation you do when checking whether two endpoints
    agree about which records exist.

    Why bother: the moment you have data from two places — an API and your
    database, yesterday's export and today's, two endpoints that ought to
    agree — somebody asks whether they match. Answering it with nested loops
    is slow and unreadable. Sets answer it directly: they support subtraction
    ("in this one but not that one") and intersection ("in both"), each as a
    single operator. Converting to sets also collapses duplicates on the way
    in, which is why the third example folds `[1,1,2]` down to one `1`.

    The reason the answer comes back as sorted lists rather than sets is
    ordinary practicality: a set prints in an unpredictable order, so the same
    correct answer would look different from one run to the next and could not
    be compared against an expected value in a test.
    """
    # TODO
    raise NotImplementedError


def running_total(numbers):
    """Return the cumulative sums.

    Walk the list once and, at each position, return the total of everything up
    to and including that point. The result is a list the same length as the
    input.

    running_total([1, 2, 3])  -> [1, 3, 6]
    running_total([])         -> []
    running_total([5])        -> [5]

    Why bother: this is a running balance — cumulative revenue by day, total
    downloads to date, a bank account after each transaction. If SQL is your
    background you have written it as a window function; here you do it by
    hand, which makes it obvious what the window function was doing.

    The technique is worth naming because it recurs everywhere: keep one
    variable outside the loop that carries information forward from one item to
    the next. That variable is called an accumulator. Start it at zero, add
    each number to it, and record its value after every addition. Take care to
    append the running value rather than the current number.
    """
    # TODO
    raise NotImplementedError


def top_n(pairs, n):
    """Given (label, score) tuples, return the n highest-scoring labels.

    You are handed a list of two-item tuples, each pairing a label with its
    score. Rank them from highest score down and return just the labels of the
    best `n` — labels only, not the scores. If there are fewer than `n` items
    to begin with, return all of them rather than complaining.

    top_n([("a", 3), ("b", 9), ("c", 5)], 2)  -> ["b", "c"]
    top_n([("a", 1)], 5)                      -> ["a"]
    top_n([], 3)                              -> []

    Ties: when two labels have the same score, the alphabetically smaller
    label comes first.
        top_n([("b", 5), ("a", 5)], 2)  -> ["a", "b"]

    Why bother: "give me the top ten" is what people actually ask for once you
    have fetched some data — busiest endpoints, most-starred repositories,
    highest-error days. The interesting part is not the ranking, it is the tie
    rule. Without one, two items with identical scores can come out in either
    order, so your report changes between runs for no visible reason and nobody
    trusts it. Deciding the tiebreaker deliberately is what makes output
    reproducible.

    Hint: sorted() takes key=. A key that returns a TUPLE sorts by the first
    element, then the second, and so on. To sort one field descending and
    another ascending in the same pass, negate the numeric one.
    """
    # TODO
    raise NotImplementedError


def pair_with_next(items):
    """Return consecutive overlapping pairs.

    Walk the list and pair each item with the one immediately after it. The
    pairs overlap, so an item that is not first or last shows up twice — once
    on the right of one pair and once on the left of the next. A list of four
    items therefore yields three pairs.

    pair_with_next([1,2,3,4])  -> [(1,2), (2,3), (3,4)]
    pair_with_next([1])        -> []
    pair_with_next([])         -> []

    You use this to compute deltas between consecutive time-series points.

    Why bother: whenever you want change rather than level — day-over-day
    growth, the gap between two timestamps, whether a value went up or down —
    you need each reading next to the one before it. This function produces
    exactly those neighbouring pairs, and the arithmetic afterwards becomes
    trivial.

    Notice why lists of length zero and one produce no pairs at all: a pair
    needs something to come after it, and neither of those has one. If you loop
    over positions and stop one short of the end, both cases fall out on their
    own without any special-case check — which is usually a sign you have
    chosen the right loop.
    """
    # TODO
    raise NotImplementedError


def merge_sorted(a, b):
    """Merge two already-sorted lists into one sorted list.

    Both inputs are already in ascending order. Produce one list containing
    everything from both, still in ascending order.

    Do it in a single pass with two position counters -- do NOT concatenate
    and re-sort. The point is the mechanic, and it is a classic interview
    warm-up in its own right.

    merge_sorted([1,3,5], [2,4])  -> [1,2,3,4,5]
    merge_sorted([], [1])         -> [1]
    merge_sorted([1,1], [1])      -> [1,1,1]

    Why bother: `sorted(a + b)` gives the right answer, and in everyday code
    you would just write that. The reason you are doing it the long way is that
    this merge is the heart of merge sort and shows up in interviews on its own
    — and because sorting from scratch throws away the fact that both inputs
    were already ordered, whereas a merge exploits it and does far less work.

    The idea: keep a finger on the front of each list. Compare the two items
    those fingers point at, take the smaller one, and move only that finger
    forward. Repeat until one list is exhausted, then append whatever is left
    of the other — it is already sorted, so it can go on wholesale.

    One detail worth thinking about: when the two items are equal, which do you
    take? Consistently preferring the one from `a` is called a stable merge,
    and it matters once these are records rather than numbers, because it keeps
    equal items in a predictable order.
    """
    # TODO
    raise NotImplementedError


if __name__ == "__main__":
    print(chunk([1, 2, 3, 4, 5], 2))
    print(compare_id_sets([1, 2, 3], [2, 3, 4]))
    print(merge_sorted([1, 3, 5], [2, 4]))
