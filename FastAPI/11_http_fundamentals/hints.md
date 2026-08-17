# Unit 11 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you scaffolding; a couple hand over more than usual, because `urllib.parse` is a module you have never met and there is no value in you guessing at method names.*

---

### `split_url`

This one is almost entirely a matter of knowing which field of `urlparse`'s result is which, so here it is in full:

```python
parts = urlparse(url)
return {
    "scheme": parts.scheme,
    "host": parts.netloc,
    "path": parts.path,
    "query": dict(parse_qsl(parts.query)),
    "fragment": parts.fragment,
}
```

The thing to notice is `parts.netloc` where you might have expected `parts.host`. As the lesson said, "netloc" is network location, and it includes the port and any credentials as well as the hostname. There is no plain `host` field, so this is the one you want.

The other line worth reading twice is the query. `parse_qsl` gives you a list of `(key, value)` pairs, and wrapping it in `dict()` collapses that list into a dictionary. That is what makes a repeated parameter keep its *last* value — building a dictionary from pairs simply overwrites earlier keys as it goes, so `?a=1&a=2` lands on `{"a": "2"}`. You are not adding logic for that rule; you are getting it from how `dict()` works. `parse_qsl` also decodes percent-escapes on the way through, which is why `%20` comes back to you as a space with no effort.

---

### `add_params`

Four steps, in this order:

1. `parts = urlparse(url)`
2. `params = dict(parse_qsl(parts.query, keep_blank_values=True))`
3. For each new item: `params.pop(key, None)` when the value is `None`, else
   `params[key] = value`.
4. `parts._replace(query=urlencode(params))` then `urlunparse(...)`.

Step 2's `keep_blank_values=True` matters: without it, `parse_qsl` throws away a parameter written as `?a=` with nothing after the equals sign, and you would silently drop it from the rebuilt URL.

Step 3 is where the None rule lives. `params.pop(key, None)` removes the key if it is there and quietly does nothing if it is not — that second `None` is the default that stops it raising on a key that was never present. So one line handles both "remove it" and "it was already absent."

Step 4 has the piece that looks wrong and isn't. `_replace` is a method every named tuple has, and it makes a *copy* with one field changed. It exists because named tuples are immutable, exactly like the tuples in unit 03 — you cannot assign to `parts.query`, so instead you ask for a new `parts` that is identical except for the query. Despite the leading underscore, which normally signals "private, keep out," `_replace` is genuinely public API; the underscore is there only so that it cannot collide with a field named `replace` in somebody's tuple. Then `urlunparse` takes the six-piece tuple and glues it back into a string, which is what preserves the fragment for free.

---

### `join_path`

The move that makes this easy is to stop thinking about the URL and think only about the path. Pull the URL apart, do all your work on `parts.path` as an ordinary string, then reassemble — and the query string survives without you handling it at all.

```python
path = parts.path
for part in raw_parts:
    if not part:
        continue
    path = path.rstrip("/") + "/" + str(part).strip("/")
```

The slash handling is the whole exercise. `rstrip("/")` takes trailing slashes off what you have so far, `strip("/")` takes them off both ends of the segment you are adding, and then you put back exactly one slash between them. Whatever the caller supplied — trailing, leading, both, neither — you end up with one.

`if not part: continue` covers both an empty string and `None` in a single condition, since both are falsy. That is unit 01's truthiness again.

And note what happens with no segments at all: the loop body never runs, `path` is untouched, and the URL comes back exactly as it went in. That is why `join_path("https://x.com/")` keeps its trailing slash rather than having it stripped — you only strip inside the loop, and the loop did not happen.

---

### `classify`

Do the category first, with a chain of range checks on `status`. Then the two booleans are one expression each:

```python
retryable = code == 429 or 500 <= code < 600
our_fault = 400 <= code < 500
```

Read `retryable` as the sentence the docstring was making: retry when the server broke, *or* when the server told you to slow down. 429 is the special case bolted onto an otherwise clean rule, and that is exactly why it is worth writing out rather than deriving from the category.

Watch the boundary on `"unknown"`. Since 100–199 has its own name, `"informational"`, the unknown branch only catches codes below 100 or 600 and above. If you write your chain as a series of `if`/`elif` from lowest to highest with a final `else`, that falls out correctly — but check the 100 case, because it is the one people forget to give a name.

---

### `build_auth_headers`

Start with the dictionary containing the two entries that are always there, then add two `if` statements on top of it.

Use `if token:` rather than `if token is not None:`. The plain truthiness test treats an empty string as absent, which is precisely the behaviour the docstring asks for, and it costs you nothing. This is one of the rare places where truthiness is the *right* choice rather than the risky one — because unlike a count, an empty credential is genuinely meaningless.

---

### `parse_link_header`

Splitting on `","` is fragile because URLs can contain commas. Use a regex instead:

```python
import re
PATTERN = re.compile(r'<([^>]*)>\s*;\s*rel\s*=\s*"?([^",;\s]+)"?')
return {rel: url for url, rel in PATTERN.findall(value or "")}
```

Take that pattern apart once, because it is more readable than it looks. `<([^>]*)>` means "a literal `<`, then capture everything that isn't a `>`, then a `>`" — that is the URL, and it works no matter what punctuation is inside it, commas included. `\s*;\s*` allows any amount of whitespace around the semicolon. `rel\s*=\s*` matches `rel=` with optional spaces. And `"?([^",;\s]+)"?` captures the relation name, with the surrounding quotes marked optional so it copes with servers that omit them. The parentheses are what makes each part a *capture* — `findall` returns one tuple per match containing exactly the captured pieces, in order, which is why the comprehension unpacks them as `for url, rel in ...` and then flips them round to build `{rel: url}`.

Two things this buys you. Extra parameters after `rel` are ignored automatically, because the pattern simply stops matching once it has what it wants. And a malformed entry never matches at all, so `findall` skips it — which satisfies "malformed entries are skipped rather than raising" without a single line of error handling.

The `value or ""` at the end is the small guard that handles both the empty-string and the `None` inputs in one go, since `findall` would raise on `None`.

---

### `next_page_url`

`return parse_link_header(link_header).get("next")`

That is the whole function. `.get()` rather than square brackets is doing the work: when there is no next page, GitHub simply omits that entry, and `.get()` hands you `None` instead of raising — which is exactly the answer the docstring asks for.

---

### `seconds_until_reset`

Normalise the keys before you do anything else, so that the rest of the function can assume lowercase:

```python
lower = {k.lower(): v for k, v in headers.items()}
```

That is unit 04's dictionary comprehension for rewriting keys, and it is the entire answer to the case-insensitivity problem. One line at the top beats checking three spellings at every lookup.

Then work through the three rules in order, returning as soon as one applies. Rule 1 looks for `"retry-after"`, rule 2 for `"x-ratelimit-remaining"` and `"x-ratelimit-reset"`, and rule 3 is just `return 0` at the bottom.

Wrap each `int()` conversion in `try`/`except ValueError`. This is not defensive paranoia — `Retry-After` is genuinely allowed to hold an HTTP date instead of a number of seconds, and the last test hands you exactly that. Converting `"Wed, 21 Oct 2015 07:28:00 GMT"` to an integer raises `ValueError`, and what you want is to fall through to rule 2 rather than crash. Catching the error and continuing is the whole reason unit 08 exists.

Finally, `max(0, reset - now_epoch)`. The subtraction is what turns an absolute timestamp into a duration, and the `max` handles a reset time that has already gone past, which would otherwise hand your caller a negative sleep.
