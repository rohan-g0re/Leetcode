# Unit 02 — hints

*Open this after roughly ten minutes of genuine effort on a function, not before. These give you the approach and the reasoning, not the finished answer — the typing is still yours, and the typing is where it sticks.*

---

### `normalize_key`

The whole function turns on one convenient behaviour: `.split()` called with **no argument at all** splits on any run of whitespace and quietly throws away the empty pieces. So `"  total   count  ".split()` gives you `["total", "count"]` — the leading spaces, the trailing spaces and the triple gap in the middle have all been dealt with in one call, for free.

That handles spaces. It does nothing about hyphens, so the move is to make hyphens *look* like spaces before you split, and then let the split clean them up along with everything else.

```python
spaced = raw.replace("-", " ")
parts = spaced.split()
```

The reason this works so neatly is that you have converted a two-kinds-of-separator problem into a one-kind-of-separator problem, and then used the tool that is already perfect at the remaining kind. Once you have the list of parts, lowercase them and join with `"_"`.

The empty case needs no special handling, which is worth noticing. `"".split()` gives you an empty list, and joining an empty list gives back `""`. The rule you wrote for the normal case already covers the edge case, so resist the urge to add an `if` for it.

---

### `parse_iso_date`

This one is a chain of checks, and the useful discipline is to fail early rather than write one enormous condition. Each step below either rules the input out or hands a smaller problem to the next step.

First, refuse anything that is not text at all, because every string method you are about to call would explode on `None`:

```python
if not isinstance(text, str):
    return None
```

`isinstance(value, str)` asks "is this thing a string?" and is the standard way to check a type in Python.

Next, throw away the time portion. Splitting on `"T"` and taking the first piece works whether or not there was a `T` — if there wasn't, the split gives you a one-item list and you take the only item, unchanged. That is why `text.split("T")[0]` is safe on both `"2024-01-05"` and `"2024-01-05T10:30:00Z"` without an `if`.

Then split the remainder on `"-"` and insist that you got exactly three pieces, and that every piece is entirely digits:

```python
parts = text.split("T")[0].split("-")
if len(parts) != 3:
    return None
if not all(p.isdigit() for p in parts):
    return None
```

`all(...)` is `True` only when every item it is given is true, so this rejects the whole date if any single piece is bad. That one line also quietly rejects empty pieces, because `"".isdigit()` is `False` — which is exactly what you want for something like `"2024--05"`.

Everything that survives those checks is genuinely three numbers, so the last step is just conversion: `int()` each part and return them as a tuple.

---

### `truncate`

Split your thinking into two cases and the function almost writes itself.

The easy case is when the text already fits, `len(text) <= limit`, and there you return it exactly as it came in — no dots, no changes.

The interesting case is when it does not fit. You want the result to be exactly `limit` characters, of which the last three are dots, so you may keep `limit - 3` characters of the original:

```python
return text[: limit - 3] + "..."
```

That works whenever `limit` is 3 or more. Below that it goes wrong, and it is worth understanding *how* it goes wrong rather than just patching it: with `limit = 2` the slice becomes `text[:-1]`, and a negative number in a slice counts backwards from the end, so instead of taking nothing you take almost everything. Python has not made a mistake there; you just asked it a different question than you meant to.

So handle the small limits deliberately, before that line:

```python
if limit <= 3:
    return "..."[:limit]
```

Slicing the dots themselves gives `"..."` at 3, `".."` at 2, and `""` at 0 — every small case, with no arithmetic and nothing to get backwards.

---

### `extract_domain`

Start with the rejection, since it is a single line and it means everything after it can assume it is looking at a URL:

```python
if "://" not in url:
    return None
```

Now get the part after the scheme. `url.split("://")` gives you two pieces and you want the second one, `[1]`.

What is left starts with the host but may have a path or a query stuck on the end. The trick is that splitting and taking the first piece works whether or not the separator is present:

```python
rest = url.split("://")[1]
host = rest.split("?")[0].split("/")[0]
```

Do the `?` first and the `/` second, then lowercase the result. This reads as "cut off the query if there is one, then cut off the path if there is one" — and because `.split()` on a string with no separator returns a one-item list, the "if there is one" is handled without you writing a single condition. That is the pattern to remember: `split(x)[0]` means "everything up to the first x, or all of it."

---

### `build_query_string`

Build the pieces, then join them:

```python
pairs = [f"{k}={v}" for k, v in params.items() if v is not None]
return "&".join(pairs)
```

The square brackets with a `for` inside are a list comprehension, covered properly in unit 07 — read it for now as "make a list, one `f"{k}={v}"` for every key and value in params, but skip the ones where the value is None." The f-string converts the values to text as it goes, so you do not need a separate `str()` call.

The load-bearing detail is `is not None` rather than just `if v`. Those are not the same test. `if v` skips anything Python considers empty, which includes `0` and `""` — so a page number of 0 would silently vanish from your request and you would get page 1 back with no error and no clue why. The test case `{"x": 0}` exists purely to catch that, and it catches a lot of people.

If comprehensions still feel alien, write it as an ordinary loop with an `if` and an `.append()` first. It is the same thing and it costs you three lines.

---

### `title_words`

Define the punctuation once, as a plain string, because `.strip()` takes a string of characters and removes any of them from either end:

```python
PUNCT = ".,!?:;\"'()[]"
```

The backslash before the double quote is there so Python does not think the string ends at that point — that is the escaping from the lesson, doing its job.

From there it is one pass over the words: split the text on whitespace, strip the punctuation off each piece, lowercase it, and keep it only if its length is now at least `min_length`. Collect the survivors into a `set` rather than a list, because a set refuses to store the same value twice and so removes your duplicates without you writing any comparison logic. Then `sorted(that_set)` hands you back a plain list in alphabetical order.

Order the operations as strip, then lowercase, then measure. Measuring before stripping counts the punctuation as part of the word and lets four-letter words through on a five-character technicality.

---

### `format_table_row`

`zip(cells, widths)` walks two lists in step, giving you the first cell with the first width, the second with the second, and so on. That is the shape you want, because each cell needs its own width and nothing else.

```python
padded = [f"{cell:<{width}}" for cell, width in zip(cells, widths)]
return " | ".join(padded).rstrip()
```

Two things are doing work in that f-string. The `<` means left-align, and the inner `{width}` means "take the width from this variable" rather than typing a fixed number — which is the only reason this function can handle any column layout instead of one hardcoded one. And because format codes pad but never cut, a cell that is too long simply comes out at full length, which is the not-truncated behaviour the spec asks for.

The `.rstrip()` at the end removes trailing spaces from the finished row. It matters more than it looks: invisible trailing whitespace is the classic reason a test says two strings differ when they look identical on screen. If you hit that, print the value with `!r` in an f-string and you will see exactly what is there.
