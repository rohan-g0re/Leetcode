# 06 — Functions

*This is the unit where your code stops being a script and starts being something a reviewer can read. About twenty-five minutes. Read it straight through — the two sections marked as the ones that matter are section 2 and section 4, and if you're short on time those two plus section 9 are the ones to slow down on. Everything assumes units 01 to 05 and nothing else.*

---

## 1. Why this unit exists at all

Up to now you've been writing code that runs top to bottom: fetch a thing, loop over it, print something. That works fine for ten lines. It stops working the moment someone asks you to do the same thing to a second URL, or asks "where exactly did the number go wrong?"

A **function** is a named, reusable block of code that takes some values in and hands a value back. That's the mechanical definition. The practical one is better: a function is a place to put a decision so that it has a name, so you can test it on its own, and so you can point at it when someone asks what it does.

Here's the frame for the whole unit. In your interview you'll be handed a live endpoint and asked to fetch data, clean it, and say something about it. Two candidates produce the identical correct answer. One writes forty lines straight down the page; the other writes three functions called `fetch_users`, `clean_records`, and `summarize`. The second scores higher every time — not because the interviewer is being aesthetic, but because they can *see* the thinking, and they can ask "what happens if the network is down?" and get an answer that isn't "the whole thing breaks." That's most of your structure score, available for free.

---

## 2. Defining, calling, and the one bug everyone hits

**This is the section that matters most in the unit.** Not because the syntax is hard — it isn't — but because it contains the single most common beginner mistake in this entire course, and it produces a wrong answer rather than an error message, which is worse.

You define a function with `def`:

```python
def greet(name):
    return f"hello {name}"

greet("rohan")        # 'hello rohan'
```

The `def` line creates a function object and binds the name `greet` to it — which is exactly unit 01's idea again, a name pointing at an object, except this time the object happens to be a piece of executable code. Nothing inside the function runs when you write the `def`. It runs when you *call* it, which is what the parentheses do. The indented block underneath is the **body**.

`return` does two things at once: it ends the function immediately, and it hands a value back to whoever called it. Anything written after a `return` in the same branch never executes. If you have a `return` inside a loop, hitting it exits the *whole function*, not just the loop — which is genuinely useful for "find the first match and stop," and occasionally surprising the first time.

Now the important part.

**A function that doesn't say `return` gives back `None`.** Not nothing, not an error — `None`, the "there is no value here" object from unit 01. Python inserts it silently. So this:

```python
def total(xs):
    print(sum(xs))       # prints to the screen, returns None

result = total([1, 2])   # prints 3, and result is None
result + 1               # TypeError: unsupported operand type(s)
```

The `print` worked. You saw `3` appear. Everything looked fine. And then `result` was `None` and the next line blew up somewhere else entirely, which is why this bug is so annoying to track down — the error surfaces far away from the mistake.

Say this to yourself once and keep it: **printing is not returning.** `print` shows a value to a human being looking at a terminal. `return` gives a value to the code that called you, so it can do something with it. They are unrelated operations that happen to look similar when you're testing by eye. Every function in this course's tasks wants a `return`, and every test file checks the returned value, so a `print`-only function fails every single test while looking, to you, like it works.

Here's the practitioner's detail that explains why this trips people up so persistently. If you're poking around in the interactive Python prompt, typing an expression echoes its value automatically. So `total([1, 2])` at the prompt shows you `3` — and you conclude your function returns 3. It doesn't; you're seeing the `print`. The illusion only breaks the moment you assign the result to a variable, which is exactly what the test file does and exactly what you didn't do while checking. When a function "works when I run it" but fails its test, look for a missing `return` before you look anywhere else.

When you need to hand back more than one thing, return a tuple — several values separated by commas — and unpack them on the other side:

```python
def stats(xs):
    return min(xs), max(xs), sum(xs) / len(xs)

lo, hi, mean = stats([1, 2, 3])
```

The mental model for this whole section: **a function is a machine that eats arguments and emits one value; if you don't tell it what to emit, it emits `None`.**

---

## 3. Parameters, arguments, and defaults

Two words that get used interchangeably and shouldn't be. A **parameter** is the name in the `def` line — the slot. An **argument** is the actual value you pass in when you call. `def fetch(url)` declares a parameter called `url`; `fetch("http://x")` passes an argument.

You can give a parameter a **default value**, which makes it optional at the call site:

```python
def fetch(url, timeout=10, retries=3):
    ...

fetch("http://x")                        # positional
fetch("http://x", 30)                    # positional
fetch("http://x", timeout=30)            # keyword — clearer
fetch("http://x", retries=5, timeout=1)  # keyword order doesn't matter
```

Passing by position means Python matches your arguments to parameters in order. Passing by **keyword** means you name the parameter explicitly, which frees you from order entirely. Parameters with defaults must come after parameters without them, because otherwise Python couldn't work out what a bare positional argument was meant for.

The habit worth forming: use keyword arguments at the call site for anything that isn't obvious. `fetch(url, 30, 5)` is a puzzle a week later — is 30 the timeout or the retry count? `fetch(url, timeout=30, retries=5)` documents itself and costs you nine characters. Reviewers notice.

---

## 4. The mutable default trap

**This is the other section that matters, and it's the one interviewers actually ask about.** It's also, satisfyingly, just unit 01's "names point at objects" idea coming back to collect.

Look at this and predict the output before reading on:

```python
def add_item(item, basket=[]):      # WRONG
    basket.append(item)
    return basket

add_item("a")    # ['a']
add_item("b")    # ['a', 'b']   <- what?
add_item("c")    # ['a', 'b', 'c']
```

Every call was supposed to start with an empty basket. Instead the basket keeps everything from every previous call. This looks like Python being broken. It isn't, and once you see why, you'll never write it again.

Here's the why. **The default value is evaluated once, when the `def` line runs — not each time you call the function.** When Python read that `def`, it built one empty list, right then, and attached it to the function object as its stored default. There is exactly one list in this story. Every call that doesn't supply a basket gets a name bound to *that same list*, appends to it, and hands it back. You're not getting a fresh empty list per call; you're getting three labels on one list, which is the same thing that happened in unit 01 when `b = a` changed `a`.

The practitioner's detail: you can actually see it. The default lives on the function object under `add_item.__defaults__`, and if you print that after each call you'll watch the list grow. Nothing is hidden — it's just stored in a place you weren't looking.

Note also that this only bites for **mutable** values, meaning things that can be changed in place: lists, dictionaries, sets. A default of `0` or `"none"` or `None` is perfectly safe, because you *cannot* modify those in place — any operation on them produces a new object, so there's nothing to accumulate.

The fix is a two-line ritual, and you should type it enough times that it becomes automatic:

```python
def add_item(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item)
    return basket
```

`None` is immutable and shared, so nothing can accumulate on it. The `if` runs on every call, so the list is genuinely built fresh each time. And notice the check is `is None`, not truthiness — because a caller who legitimately passes an empty list `[]` should get their own list back, mutated, not silently swapped for a new one. That distinction is exactly unit 01's "is there anything here?" versus "was this field supplied?" and unit 06's task tests both halves of it.

The rule, and the mental model: **never use a mutable default; the `def` line runs once, so `[]` in a signature is one list for the lifetime of your program.**

`add_tag` in `task.py` exists purely so you write this fix with your own hands. The second assertion in its docstring is the entire point of the exercise.

---

## 5. `*args`, `**kwargs`, and keyword-only parameters

Sometimes you don't know in advance how many arguments a function will get. Two pieces of syntax handle that.

```python
def f(*args, **kwargs):
    print(args)      # a TUPLE of the extra positional arguments
    print(kwargs)    # a DICT of the extra keyword arguments

f(1, 2, a=3)         # (1, 2)   {'a': 3}
```

A parameter written with one star collects every leftover positional argument into a tuple. A parameter written with two stars collects every leftover keyword argument into a dictionary, where the keys are the parameter names the caller typed. The names `args` and `kwargs` are pure convention — the stars are what Python actually reads — but use them anyway, because everyone expects them.

The commonest real use is **forwarding**: writing a thin wrapper that passes options through to something else without having to list them all.

```python
def get_json(url, **params):
    r = requests.get(url, params=params, timeout=10)
    return r.json()

get_json("https://api.x.com/search", q="python", page=2)
```

The same stars work in the other direction, at the call site, where they mean "unpack this collection into separate arguments":

```python
args = [1, 2]
opts = {"timeout": 5}
f(*args, **opts)          # exactly the same as f(1, 2, timeout=5)
```

That's the same `**` you met in unit 04 merging two dictionaries — same idea, spread this thing's contents into what I'm building.

The practitioner's detail worth having: `**kwargs` preserves the order the caller typed them in, because dictionaries have kept insertion order since Python 3.7. That's what lets `build_url` in your task promise that query parameters come out in the order they were passed. Before 3.7 that promise would have been a lie.

Finally, a bare `*` in a signature means "everything after this must be passed by keyword":

```python
def slice_data(records, *, limit=10, offset=0):
    ...

slice_data(rows, limit=5)     # fine
slice_data(rows, 5)           # TypeError
```

Use it for options that would be meaningless as bare positional values — nobody should have to guess what the `5` in `slice_data(rows, 5)` means. You already met this in unit 04's `deep_get(data, *keys, default=None)`, where it was doing real work: the stars swallow every path segment, so the only way to specify a default is by name.

---

## 6. Scope, and the thing that makes `make_counter` work

**Scope** is the region of code where a name is visible. Names assigned inside a function are **local** to it: they exist while the function runs and vanish when it returns.

```python
def f():
    x = 1          # local to f
    print(x)

f()
print(x)           # NameError: x is not defined
```

Reading a name from outside works fine. *Assigning* to it is where it gets strange:

```python
count = 0

def bump():
    count = count + 1     # UnboundLocalError!
```

Python scans the whole function body before running it, sees an assignment to `count`, and decides `count` is local for the entire function — including the read on the right-hand side, which now happens before anything has been assigned to it. The name `global count` fixes it, and you almost never want `global`. A function that quietly reads and writes module-level state is hard to test and hard to reason about, which is precisely the thing interviewers probe for. Pass values in, return values out.

The lookup order has a name worth knowing because the error messages assume it: **LEGB** — Local, then Enclosing (an outer function wrapping this one), then Global (the module), then Builtins (`len`, `sum`, and friends).

The "Enclosing" step is the one your task needs. When you define a function *inside* another function, the inner one can still see the outer one's variables — and it keeps seeing them even after the outer function has finished and returned. An inner function that hangs on to a variable from its enclosing function like this is called a **closure**.

```python
def make_greeter(greeting):
    def greet(name):
        return f"{greeting}, {name}"
    return greet

hi = make_greeter("hello")
hi("rohan")               # 'hello, rohan'
```

`make_greeter` has finished running by the time you call `hi`, yet `greeting` is still there. The inner function holds a reference to it, so it stays alive.

Reading an enclosing variable works out of the box. *Assigning* to one hits the same rule as before — the assignment makes the name local to the inner function — and the keyword that fixes it is `nonlocal`, not `global`. `global` reaches all the way out to module level; `nonlocal` reaches out exactly one layer to the enclosing function. That's the keyword `make_counter` in your task is hinting at, and the alternative hint in that docstring is worth understanding too: if you keep the state in a mutable container, like a one-element list, you can *modify* it without ever *rebinding* the name, so the rule never triggers. Names versus objects, one more time.

---

## 7. Functions are objects you can pass around

A function is a value like any other. You can store it in a variable, put it in a list, pass it as an argument, and return it from another function. That's not a clever trick in Python — it's the ordinary state of affairs, and several things in this course depend on it.

```python
def double(x):
    return x * 2

f = double          # no parentheses: the function itself
f(5)                # 10

sorted(records, key=lambda r: r["score"])    # a function passed as an argument
```

The distinction to burn in: `double` is the function object. `double()` *calls* it and evaluates to whatever it returns. Leaving the parentheses off when you meant to call, or adding them when you meant to pass the function along, is a slip everyone makes, and the resulting error usually looks unrelated — something like `'function' object is not subscriptable`, which is Python telling you that you tried to index a function.

You've already relied on this. In unit 05, `collect_pages(fetch_page)` took a function as an argument so the paging logic didn't have to know anything about how a page gets fetched. That pattern — **inject the thing that does the I/O** — is how you make network code testable without a network, and it's coming back hard in Part 2.

Three of this unit's task functions live entirely here. `apply_to_field` takes a cleaning function and applies it to one field of every record — which is the same shape as pandas' `.apply()` and the same shape as `sorted(key=...)`. Note that you can pass `str.strip` directly as that function: methods are just functions that take the object as their first argument, so `str.strip("  a ")` works exactly like `"  a ".strip()`. `retry_call` takes a function and decides *when* to run it, which is the core of every retry helper ever written. And `compose` takes several functions and returns a new one that runs them in sequence — a cleaning pipeline built out of parts.

The mental model: **a function name without parentheses is a noun; with parentheses it's a verb.**

---

## 8. Docstrings and type hints

Two small things that cost seconds and read as professional.

```python
def average(values: list[float], default: float | None = None) -> float | None:
    """Return the mean of `values`, or `default` when the list is empty."""
    if not values:
        return default
    return sum(values) / len(values)
```

The string on the first line of the body is a **docstring** — a description Python stores and can show you later via `help(average)`. Write one for every function you define in an interview.

The `: list[float]` and `-> float | None` bits are **type hints**: annotations saying what goes in and what comes out. They are *not enforced* at runtime — pass a string where a list was promised and Python will happily try, then fail somewhere further down. Hints exist for readers, editors, and checking tools. The one enormous exception is Part 4: Pydantic and FastAPI read your hints and enforce them, turning them into real validation and real API documentation. That's exactly why FastAPI feels like magic, and why getting comfortable writing hints now pays off later.

---

## 9. The three-function shape for an interview answer

This is the structural payoff of the whole unit, and it's worth memorizing as a shape rather than as advice.

```python
def fetch(...):        # touches the network. Nothing else.
def transform(raw):    # pure: data in, data out. No I/O.
def summarize(rows):   # pure: the actual answer.
```

A function is **pure** when it only looks at its arguments and only produces a return value — no network calls, no file reads, no changing anything outside itself. `fetch` is deliberately impure and deliberately tiny. Everything else is pure.

Why this split earns points. First, `transform` and `summarize` become testable with a hardcoded dictionary — you can prove your logic works in one second without waiting for a network or worrying that the API is rate-limiting you. Second, when the answer comes out wrong you can bisect: print the raw response, and you instantly know whether the data was bad or your logic was bad. Without the split, those two failures look identical. Third, it's the boundary every reviewer is looking for, and saying *why* you drew it out loud is a free point.

If SQL is your background the split will feel familiar: `fetch` is the query that pulls rows out, `transform` is your `SELECT` list cleaning columns, and `summarize` is the `GROUP BY` with the aggregates. You already separate those instinctively in SQL. This is the same discipline.

One detail that catches people, and it connects straight back to section 4. `transform` should build *new* records rather than modifying the ones it was handed — `{**record, "field": cleaned}` makes a copy, whereas `record["field"] = cleaned` edits the caller's data underneath them. That's the names-and-objects thread again, and `apply_to_field` in your task tests it explicitly: the originals must come out unchanged.

The target shape coming out of `transform` is the one this course keeps aiming at — a list of flat dictionaries. Everything downstream, from `csv` to pandas to FastAPI's JSON response, accepts that shape without complaint.

---

## 10. What I have deliberately left out

A few tools that belong to this unit aren't explained here, and that's on purpose. Reading documentation under mild time pressure is the most transferable skill in this whole course, and a lesson that hands you everything can never teach it. In an interview nobody minds you looking something up; they mind you *guessing*. So go find these — `help()` at the interactive prompt is faster than a web search for most of them.

`functools.lru_cache` is a **decorator** — a line starting with `@` written above a `def` that wraps your function in extra behaviour — and this particular one **memoizes**, meaning it remembers what your function returned for a given set of arguments and hands back the stored answer instead of recomputing. Unit 22 uses it properly; look now at what it does to a function you call twice with the same URL. `functools.partial` is worth five minutes for how it pre-fills some arguments and gives you back a new function. `map()` and `filter()` are the older way of applying a function across a collection — find out why comprehensions in unit 07 are usually preferred. Work out what a `lambda` cannot contain, which is the reason it stays a one-liner. And `inspect.signature(f)` will show you a function's parameters at runtime, which is a genuinely useful thing to know exists.

---

## 11. Check yourself

Answer these before opening the task. If one isn't obvious, reread the section — that's much cheaper than getting stuck halfway through `make_counter` and not knowing why.

1. What does a function without a `return` give back?
2. Why is `def f(items=[])` dangerous, and what's the fix?
3. What's the difference between `f` and `f()`?
4. What does `*args` collect, and what type is it?
5. Why does assigning to a global name inside a function raise `UnboundLocalError`?
6. Which keyword lets an inner function assign to a variable from the enclosing function?
7. Why separate `fetch` from `transform`?

*(Answers: 1. `None`. 2. the default is created once, when the `def` line runs, so every call that doesn't supply one shares the same list; default to `None` and build the list inside the body. 3. `f` is the function object itself; `f()` calls it and evaluates to what it returns. 4. the extra positional arguments, as a tuple. 5. the assignment makes the name local for the entire function, so the read on the right-hand side happens before anything is bound to it. 6. `nonlocal` — `global` reaches to module level, which is one layer too far. 7. so the pure logic is testable with hardcoded data and no network, and so a wrong answer can be traced to either bad data or bad logic rather than both at once.)*

---

*Three things to carry out of this unit. Printing is not returning — a function with no `return` hands back `None`, and that mistake produces a wrong value rather than an error, which is why it costs people so much time. A mutable default is evaluated once when the `def` runs, so `items=[]` is one list shared across every call, which is unit 01's names-point-at-objects idea wearing a different hat, and the same idea is why `transform` must copy records instead of editing them. And the fetch / transform / summarize split is the shape of a good answer: quarantine the network in one small function so everything else is pure, testable in a second, and explainable out loud. Unit 07 takes the "pass a function as an argument" thread and turns it into comprehensions and `lambda`.*

*Now open [`task.py`](task.py).*
