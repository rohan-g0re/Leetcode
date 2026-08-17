# 05 — Control Flow: Loops and Decisions

*This is the unit where your code stops handling one record and starts handling five hundred. Read it straight through — about twenty minutes — then open `task.py`. Two things here carry more weight than the rest: how Python's `for` loop actually works, and the shape of the `while` loop that walks through a paginated API. Everything else is supporting cast. Nothing is assumed beyond units 01 to 04.*

---

## 1. Why this unit exists

Unit 04 ended with the shape everything in this course aims at: a list of flat dictionaries, one dictionary per record. You know how to read a field out of one record now. What you can't yet do is *say the same thing about every record without typing it five hundred times.*

That's what **control flow** means — the rules that decide which lines of your code run, and how many times. There are only two ideas in the whole topic. **Branching** is choosing between paths: do this if the status code was 200, do that if it was 429. **Looping** is repeating: do this once for every record you were handed.

If SQL is where you come from, notice that you've never had to think about either of these. A `WHERE` clause is branching, but the database writes the loop for you and hides it. `GROUP BY` is a loop with an accumulator inside it, and you never see the accumulator. Python hands you back the machinery. That's more work and considerably more power — you can do things inside a Python loop that no `WHERE` clause could express, like "call an API, and if it says slow down, wait and try again."

The interview version of this: you'll be handed an endpoint and asked to summarize what came back. Every single answer to that question is a loop with a condition inside it.

---

## 2. Indentation is not decoration

Before any of that, one piece of syntax that is genuinely unlike most languages. Python has no curly braces around blocks of code. It uses **indentation** — the blank space at the start of a line — and that space is real, meaningful syntax that the interpreter reads.

A line ending in a colon opens a block. Every line indented underneath it belongs to that block. Going back out to the left closes it.

```python
if x > 0:
    print("positive")
    print("still inside the if")
print("outside — this runs no matter what")
```

The first two prints only happen when `x` is positive. The third always happens, because it's back at the left margin. That's the entire rule.

Use **four spaces** per level, always. Not two, not a tab. Python will actually refuse to run a file that mixes tabs and spaces in the same block — it raises `TabError` — and the maddening part is that tabs and spaces look identical on screen, so you'll be staring at code that looks perfect. Set your editor to insert spaces when you press Tab and then never think about this again. VS Code does it for Python by default.

The two errors you'll meet in your first hour are `IndentationError: unexpected indent` (you indented something that shouldn't be) and `expected an indented block` (you wrote a colon and then didn't indent the next line). They mean exactly what they say, which is not something you can rely on with every Python error message.

The mental model: **the colon opens a room, the indentation is the room, and stepping back to the left is walking out of it.**

---

## 3. `if`, `elif`, `else` — and the habit reviewers look for

Branching looks like this, and it's about as surprising as you'd expect:

```python
if status == 200:
    kind = "success"
elif status == 404:
    kind = "not found"
elif status >= 500:
    kind = "their problem"
else:
    kind = "something else"
```

`elif` is one word — it's short for "else if" — and it matters that **only the first matching branch runs.** Python checks them top to bottom and the instant one is true it executes that block and skips every branch below it, even if those would also have been true. That ordering rule is not trivia. It's the whole trick in the `classify_status` function you're about to write: the code `429` is a client error *and* a rate limit, so the rate-limit branch has to come first or it can never fire. Same with FizzBuzz in the same task — a multiple of both 3 and 5 has to be tested before either individual case, or the "both" branch is unreachable code that can never run.

**Guard clauses — this is the habit worth taking away.** When you're validating a record, the instinct is to nest: check it's not `None`, and inside that check it has an id, and inside that check the id is positive. Three levels deep and each new condition pushes everything further right.

```python
def process(record):
    if record is not None:
        if "id" in record:
            if record["id"] > 0:
                return do_work(record)
    return None
```

Turn it inside out. Handle each *bad* case first and return immediately, so that by the time you reach the bottom of the function everything left is valid:

```python
def process(record):
    if record is None:
        return None
    if "id" not in record:
        return None
    if record["id"] <= 0:
        return None
    return do_work(record)
```

Same behaviour, and it reads down the page as a list of reasons to bail out, with the real work sitting flat and unindented at the bottom. Each of those early `return` statements is a **guard clause**. Write it this way and a reviewer watching you code will notice — this is one of the small things that reads as experience rather than book learning. It also pairs directly with unit 04's world of missing fields: most of your guards will be `.get()` came back `None`, so leave now.

There's also a one-line form for the simple case, called a **conditional expression** or ternary:

```python
label = "high" if score > 50 else "low"
```

Read it value-first: *this* value if the condition holds, otherwise *that* one. It's backwards from how most languages write it and backwards from how you'd say it out loud, which is why it looks odd for about a day. It's fine when it fits comfortably on one line. When you start reaching for it with three conditions chained together, stop and write a real `if`.

Python 3.10 added a `match` statement for matching a value against several shapes at once. It's genuinely nice occasionally, and you will almost never need it — an `if` chain or a dictionary lookup is clearer for the things you'll be doing. Recognize it when you read someone else's code and move on.

---

## 4. `for` — the section that matters most

**What it is.** This is where Python is properly different from other languages, so read it slowly even if you've written loops elsewhere.

In most languages, a `for` loop is a counter: start `i` at zero, keep going while `i` is less than the length, add one each time, and use `i` to look things up. Python has no such construct. Python's `for` walks over the **elements themselves**. There is no counter anywhere unless you deliberately ask for one.

```python
for item in [10, 20, 30]:
    print(item)          # prints 10, then 20, then 30
```

`item` is a name that gets rebound to each element in turn — and that's unit 01's idea again, a name pointing at an object rather than a box holding one. First time round the loop, `item` points at `10`. Second time, at `20`. The loop body runs once per element and then it's over.

**Why it exists in this form.** Because the same statement then works over *everything*, with no variation:

```python
for char in "abc": ...                    # each character
for record in records: ...                # each dictionary in a list
for key in {"a": 1}: ...                  # each key of a dictionary
for k, v in {"a": 1}.items(): ...         # each key/value pair, unpacked
```

That last line combines unit 04's `.items()` with unpacking — `.items()` hands out pairs, and writing two names in the loop header splits each pair across them automatically. One loop form covering lists, dictionaries, strings, files, and everything else is the payoff for giving up the counter.

**Where this shows up.** Almost every data question you'll be asked is a `for` over records with an accumulator outside it. The shape looks like this and you'll write it constantly:

```python
total = 0
for record in records:
    value = record.get("followers")
    if value is None:
        continue
    total += value
```

Three things worth naming there. The accumulator `total` is created *before* the loop, because anything created inside gets rebound every pass and won't survive. The `.get()` is unit 04's habit — real records are missing fields, and this loop has to survive record 437 having no `followers` key. And `continue` skips straight to the next iteration, which is the loop-flavoured version of the guard clause from section 3.

The practitioner's detail: **the loop variable outlives the loop.** After that loop ends, `record` is still a live name pointing at the last record processed, and `value` is still whatever it was on the final pass. Python does not clean up after a `for`. This bites when you reuse a name — write a second loop over the same list using `record` again, or accidentally read `value` after the loop expecting something else, and you'll get stale data with no error at all. If a variable after a loop holds something inexplicable, this is usually why.

The mental model: **Python's `for` hands you the things, not their positions — so if you find yourself computing a position, ask what you actually wanted.**

---

## 5. When you really do need a number: `range`, `enumerate`, `zip`

Sometimes you want counting, not elements. `range` produces a run of integers.

```python
range(5)          # 0 1 2 3 4         stop only
range(2, 5)       # 2 3 4             start, stop
range(0, 10, 2)   # 0 2 4 6 8         start, stop, step
range(5, 0, -1)   # 5 4 3 2 1         backwards
```

The stop value is always excluded — the same half-open convention as slicing in unit 03, which is why `range(len(xs))` lands exactly on the valid indexes of `xs` and never one past the end. That consistency is deliberate.

`range` is **lazy**, meaning it doesn't build the list of numbers; it hands them out one at a time as the loop asks. So `range(10_000_000)` is instant and uses almost no memory. If you want to *see* the numbers, wrap it: `list(range(5))`.

Now, the beginner's move is `for i in range(len(items))` and then `items[i]` on the next line. Resist it. If you want the value, loop over the values. If you want the position *and* the value — which is what you nearly always actually want — use `enumerate`:

```python
for i, item in enumerate(items):
    print(i, item)

for i, item in enumerate(items, start=1):
    print(f"{i}. {item}")            # 1-based, for showing humans
```

You need exactly this in the task's `find_index_of_drop`, where you have to return the *position* of the first value lower than the one before it. Position is genuinely the answer there, so counting is genuinely justified.

`zip` walks two or more sequences side by side, handing you one item from each:

```python
for name, score in zip(names, scores):
    ...
```

And `zip` has a sharp edge worth knowing before it cuts you: **it stops at the shortest input, silently.** If `names` has 100 entries and `scores` has 98 because two records were dropped upstream, `zip` gives you 98 pairs, no warning, no error, and the pairs after the missing records are all misaligned. That's a wrong answer that looks completely reasonable. When the two lists are *supposed* to be the same length, pass `strict=True` (Python 3.10 and later) and get an error instead of quiet nonsense.

Finally, you can put a transformation directly in the loop header rather than sorting beforehand:

```python
for record in sorted(records, key=lambda r: r["score"], reverse=True):
    ...
```

Unit 07 covers `key=` and `lambda` properly. For now, just note that `sorted` and `reversed` hand back something you can loop over, so the header is a fine place for them.

---

## 6. Never change a list while you're looping over it

This is the bug everyone hits exactly once, and it doesn't announce itself.

```python
for item in items:
    if bad(item):
        items.remove(item)      # broken
```

Here's what actually happens. The loop keeps an internal position counter — it's hidden, but it's there. It's at position 2, it hands you the item at position 2, you delete it, and now every element after it slides one place to the left. Then the loop advances to position 3. But the item that *was* at position 3 is now sitting at position 2, and you just walked past it without looking.

The result is that roughly half the items you meant to remove survive. Not none of them, which you'd notice — about half, which looks like your `bad()` function is flaky. People lose an hour to this.

The fix is not a cleverer loop. The fix is to stop mutating and **build a new list instead**:

```python
items = [item for item in items if not bad(item)]
```

That's a list comprehension, which is unit 07's subject; read it for now as "the items from `items`, keeping only the ones that aren't bad." It builds a fresh list and rebinds the name, so nothing is being edited underfoot.

Two extensions. The same rule applies to dictionaries and sets, though dictionaries are kinder about it — adding or removing a key mid-loop raises `RuntimeError: dictionary changed size during iteration`, a loud failure rather than a quiet wrong answer. That's unit 04, section 5, and the fix there was the same idea: loop over a snapshot with `for k in list(d.keys())`.

And the deeper reason this is confusing at all is unit 01's thread. `items.remove(...)` doesn't produce a new list — it edits the one list that exists, in place, and the loop is holding that same object. If a variable were a box, this would be someone else's problem. Because a variable is a name pointing at an object, and the loop points at the same object you're editing, it's yours.

The mental model: **read a collection or edit it, never both at once.**

---

## 7. `while` and the shape of pagination

**What it is.** A `for` loop runs once per element of something you already have. A `while` loop runs as long as a condition stays true, and you use it when *you don't know how many times*. In this course that means almost exactly one thing: pagination.

**Why it exists.** APIs don't hand you ten thousand records in one response. They hand you page 1, and you ask for page 2, and you keep going until they stop giving you anything. You cannot write that as a `for` loop, because you have no idea in advance how many pages there are — the server does, and it only tells you by eventually returning nothing. That's the definition of a `while`.

```python
page = 1
results = []
while True:
    batch = fetch_page(page)
    if not batch:
        break
    results.extend(batch)
    page += 1
    if page > 50:
        break
```

Walk it. `while True` means "loop forever" — the condition is literally always true — so all the exiting is done by `break`, which quits the loop immediately. You fetch a page. If the batch came back empty, `not batch` is true (unit 01's truthiness: an empty list is falsy), and you're done. Otherwise `extend` glues the batch's records onto the end of `results` — note `extend`, not `append`, because `append` would give you a list of pages rather than a flat list of records, and flat is the shape you want. Then bump the page number and go round again.

**The two safety features, and this is the part that matters.** Every loop driven by external data needs both of these, and they are not the same thing.

1. **A stop condition.** Something inside must eventually become true and break out. Here that's the empty page. Without it you have an infinite loop, and with a network call in the middle, an infinite loop is not a frozen terminal — it's thousands of requests to someone else's server, a rate-limit ban, and an extremely awkward email.
2. **A hard cap.** The `page > 50` check. This one exists because the stop condition depends on the *other side* behaving correctly, and you don't control the other side. A buggy API that keeps returning page 1 forever will never give you an empty batch. The cap is what turns "their bug crashes my machine" into "their bug gives me 50 pages and stops."

New programmers write the stop condition and think they're finished. The cap is the one that separates code that has run in production from code that hasn't. Say it out loud in an interview — *"I'm capping this because I don't control their pagination"* — and you have just demonstrated a whole category of judgment in nine words.

**Where it shows up.** In unit 15, for real, against a live endpoint. But it's also the last two functions of *this* unit's task, `collect_pages` and `collect_until`, with a fake fetcher standing in for the network. The tests check the things that actually go wrong: that you start at page 1, that you never call the fetcher again after it returns empty, and that you never exceed the cap. Get the shape into your fingers here and unit 15 becomes a formality.

`collect_until` adds a third exit — stop once you have enough records — which is worth noting because it's the normal state of a real pagination loop. You end up with several reasons to stop, all checked in the same place, and over-fetching by part of a page is fine. Don't get clever about trimming mid-loop.

The mental model: **a `while` loop over someone else's data needs two brakes — one for when they say stop, one for when they don't.**

---

## 8. `break`, `continue`, and stopping early

Two words control a loop from the inside. `continue` abandons the current pass and jumps to the next element. `break` leaves the loop entirely.

```python
for r in records:
    if r.get("skip"):
        continue
    if r.get("stop"):
        break
    process(r)
```

`break` is how you search. When you're looking for the first record matching something — which is exactly the task's `first_match` — you return or break the instant you find it rather than scanning to the end. On a five-element list that's a rounding error. On a hundred-thousand-record response where the match is at position 12, it's the whole cost of the operation. And "did they stop when they found it" is a thing interviewers watch for, because it shows you're thinking about the work being done rather than just the answer.

Inside a function, `return` is even better than `break`: it exits the loop and the function together, so there's no leftover flag variable to check afterwards.

Two smaller notes. In **nested loops** — a loop inside a loop, which is what iterating pages-then-records inside each page looks like — `break` only exits the *innermost* one. To escape both, put the pair inside a function and `return`; that's cleaner than the flag variable everyone reaches for first.

And Python has a `for ... else` construct where the `else` block runs only if the loop finished *without* hitting a `break`:

```python
for r in records:
    if r["id"] == target:
        break
else:
    print("not found")
```

The name is genuinely bad — read it as "no break." Recognize it in other people's code; you never have to write it.

---

## 9. What a `for` loop is doing underneath

Sixty seconds on the machinery, because one consequence of it will confuse you otherwise.

`for x in thing` works because `thing` is **iterable**, which means it can produce its contents one at a time on request. Python asks it for an **iterator** — a little object whose entire job is to remember where you're up to — and then repeatedly asks that iterator for the next item until it signals there are none left. That single protocol is why one `for` statement covers lists, dictionaries, strings, files, `range`, and generators without knowing anything about them.

The consequence: **some iterables are one-shot.** A file handle or a generator (unit 07) has no way to rewind. Walk it once and it's exhausted. Loop over it a second time and you get *nothing at all* — not an error, not a warning, just zero iterations and an empty result. A list can be walked as many times as you like, which is why this never comes up until suddenly it does. If a second loop over the same thing mysteriously does nothing, you exhausted a one-shot iterable, and the fix is to materialize it once with `list(...)` and loop over that.

---

## 10. What I have deliberately left out

There are a handful of tools below that would make parts of this unit shorter, and I've left them out on purpose. Reading documentation while mildly under time pressure is the most transferable skill in this whole course, and a lesson that hands you everything is precisely the thing that can't teach it. So go and find these — in the interactive prompt with `help()`, or at docs.python.org. Five minutes each.

`itertools.islice()` takes the first N items of any iterable, including infinite ones, which is a different tool from slicing a list. `zip(..., strict=True)` is the fix from section 5 — check which Python version you need for it. `enumerate(..., start=1)` you've seen once; work out when 1-based numbering is right and when it quietly breaks an index. `any()` and `all()` replace an entire loop-with-a-boolean-flag with one line, and once you've seen them you'll spot the pattern everywhere. `time.sleep()` pauses your program, which is how you respect a rate limit — you'll need it in unit 15. And `while ... else` follows the same "no break" rule as section 8.

---

## 11. Check yourself

Answer these before opening the task. If one isn't obvious, reread the section it comes from — that's cheaper than getting stuck later and not knowing why.

1. What does `range(2, 10, 3)` produce?
2. Why is removing items from a list while looping over it a bug?
3. What does `zip` do when its inputs have different lengths?
4. When does a loop's `else` clause run?
5. What two safety features must a paginating `while` loop have?
6. Why might a second `for` over the same object produce nothing?

*(Answers: 1. 2, 5, 8 — start at 2, step by 3, stop before 10. 2. removal shifts the remaining elements left while the loop's internal index advances, so items get skipped — and about half of them survive, which looks like flaky logic rather than a loop bug. 3. it stops at the shortest input, silently, misaligning everything after the gap. 4. only when the loop finished without a `break` firing. 5. a termination condition and a hard iteration cap — the first for when the source behaves, the second for when it doesn't. 6. it was a one-shot iterable, a generator or a file, and walking it once exhausted it.)*

---

*Three ideas to carry out of this unit. Python's `for` walks elements rather than a counter, which is why `enumerate` exists for the rare times you genuinely need the position, and why reaching for `range(len(x))` is usually a sign you've mis-stated the problem. Never read and edit a collection at the same time — that trap is unit 01's "a variable is a name pointing at an object" showing its teeth, and building a new list is always the answer. And a `while` loop pointed at someone else's API needs two brakes, a stop condition and a hard cap, because you control only one of them. That last shape is the spine of unit 15, and the last two functions of this task are it in miniature. Unit 06 turns these loops into functions you can name, test, and reuse.*

*Now open [`task.py`](task.py).*
