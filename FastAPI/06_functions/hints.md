# Unit 06 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `average`

Do the filtering before you do any arithmetic. The rule is that `None` entries are ignored entirely, which means they must not count toward the total *and* must not count toward how many values you divide by. The cleanest way to guarantee both is to build a separate list of the values you can actually use, and then forget the original one exists:

```python
usable = [v for v in values if v is not None]
```

That is a comprehension, which arrives properly in unit 07; if you would rather stay with what you know, start with an empty list and append to it in a `for` loop, which is exactly the same thing spelled out. Either way you now have a list with no holes in it.

Then guard the empty case before dividing. `if not usable: return default` — and note this has to come first, because `sum([]) / len([])` is a division by zero and raises rather than returning anything you could inspect. Once past the guard you know there is at least one number, so `sum(usable) / len(usable)` is safe. That guard also handles both empty inputs at once: a genuinely empty list and a list that was all `None` both end up with `usable` empty, so they take the same path.

---

### `add_tag`

The entire exercise is two lines at the top of the body:

```python
def add_tag(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags
```

The reason this works is that `None` is immutable, so no matter how many times the function is called, nothing can be appended to the default and carried forward. The `if` runs afresh on every call, so `[]` is a genuinely new list each time — unlike `tags=[]` in the signature, where the `def` line runs once and that one list is reused forever.

Use `is None` rather than `if not tags`. They look interchangeable and are not: an empty list is falsy, so the truthiness version would throw away a list the caller deliberately handed you and give them a different one back. The test that says `assert result is given` is checking exactly that — `is` compares object identity, meaning "the very same object", not merely "equal contents".

---

### `build_url`

Build the string in three stages, in the same order the URL reads.

Start with the base, normalised. The base may or may not already end in a slash, and you want exactly one between segments, so strip any trailing slashes off first and then add your own separators deliberately:

```python
url = base.rstrip("/")
for part in path_parts:
    url += "/" + str(part)
```

`rstrip("/")` removes slashes from the right-hand end only, so `"https://x.com/"` and `"https://x.com"` both become the same thing and the rest of the code stops caring which you were given. The `str(part)` is what makes an integer segment legal — `"/" + 42` would raise a TypeError, and record IDs arrive as integers constantly.

Next the query parameters. `query` is an ordinary dictionary here, so loop over `query.items()`, skip any pair whose value `is None`, and build a list of `"key=value"` strings for the survivors. You do not need to do anything to preserve order — dictionaries have kept insertion order since Python 3.7, so `**query` already hands them to you in the sequence the caller typed.

Finally, only attach the query string if anything survived the filtering:

```python
if pairs:
    url += "?" + "&".join(pairs)
```

That `if` is what produces the "no `?` at all" rule for free. `"&".join(pairs)` puts an ampersand *between* items rather than after each one, so you never get a trailing separator, and the leading `?` is added once outside the join.

---

### `apply_to_field`

Loop over the records and build a new list. For each record, the very first thing you do is take a copy, and everything afterwards touches only the copy:

```python
new = dict(record)
```

`dict(record)` builds a fresh dictionary with the same key-value pairs — `record.copy()` does the same job if you prefer it. This is the line that satisfies the "originals must not be modified" test. Skipping it and writing `record[field] = ...` would edit the caller's data in place, and their list would change without them asking, which is the bug the test is watching for.

Then decide whether this record should be transformed at all. Two conditions have to hold: the field must be present, and its value must not be `None`. Both can be checked in one `if`, and if either fails you simply append the untouched copy and move on:

```python
if field in new and new[field] is not None:
    new[field] = func(new[field])
```

`func(new[field])` is where you actually call the function you were handed — the parentheses do the calling. Note that the transformed record keeps all its other fields, because you copied the whole dictionary rather than building a new one from scratch with only `field` in it.

---

### `make_counter`

You need a variable that lives in `make_counter`, an inner function that adds one to it and returns it, and then `make_counter` handing that inner function back — without calling it:

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter
```

`nonlocal` is the keyword the docstring was pointing at. Without it, `count += 1` is an assignment, and an assignment anywhere in a function body makes that name local to that function for its whole duration — so the read on the right-hand side would happen before anything had been assigned, and you would get `UnboundLocalError`. `nonlocal` tells Python this name belongs to the enclosing function, one layer out. (`global` would reach all the way to module level, which is one layer too far and would also make both counters share a single number.)

The last line is `return counter`, with no parentheses. With parentheses you would call it and return `1`.

There is an alternative that avoids the keyword entirely: make `count` a one-item list, `count = [0]`, and write `count[0] += 1`. That works because you are modifying the list's contents rather than rebinding the name `count`, so the assignment rule never fires. It is the same names-versus-objects distinction from unit 01, seen from the other side.

Each call to `make_counter` runs the body again and creates a brand new `count`, which is why `c` and `d` count independently.

---

### `retry_call`

The whole thing is a bounded loop with an early exit:

```python
for _ in range(attempts):
    result = func()
    if result is not None:
        return result
return on_error
```

`func()` with parentheses is where the caller's function actually runs — `func` on its own would just hand you the function object back and your check would never see a real result. Returning from inside the loop is what gives you "stop the instant a non-None value comes back": `return` exits the whole function immediately, so no further attempts happen.

The underscore as the loop variable is a convention meaning "I need to repeat this N times but I don't care which iteration I'm on". And the zero-attempts case needs no special handling at all, because `range(0)` is empty and `range(-1)` is empty too — the loop body never runs, execution falls straight to the last line, and `on_error` comes back with `func` never having been called. The test asserts exactly that.

---

### `compose`

You are writing a function that builds and returns another function, so the shape mirrors `make_counter`: define an inner one, then hand it out.

```python
def composed(value):
    for func in funcs:
        value = func(value)
    return value
return composed
```

The reassignment `value = func(value)` is what chains the steps together — after the first pass `value` holds the stripped string, so the second pass lowercases the stripped version rather than the original. Because the loop walks `funcs` front to back, the functions run in the order they were passed, which is the left-to-right pipeline order the docstring specifies.

`composed` can see `funcs` even after `compose` has returned, for exactly the same reason `counter` could see `count` — it is a closure over the enclosing call's variable.

The empty case comes out right on its own: with no functions, the loop body never executes, `value` is returned exactly as it arrived, and you have the identity function without writing a single special case for it.
