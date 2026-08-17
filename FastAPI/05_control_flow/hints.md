# Unit 05 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `classify_status`

Write this as one `if`/`elif`/`else` chain and put the `429` test at the very top, before any branch that catches the 400s in general. Python stops at the first branch that matches, so if a broad "anything in the 400s" test comes first it will claim `429` and the rate-limit branch below it becomes code that can never run. Nothing warns you about this — the function simply returns the wrong word.

After that it is ranges, and the thing to be careful about is that each one needs both a lower and an upper bound:

```python
if code == 429:
    ...
elif 200 <= code < 300:
    ...
```

Writing `code < 300` on its own looks like it works, and it does for every test case you would think to try by hand — until `99` or `100` comes along and is cheerfully classified as a success, because it is also less than 300. The 1xx codes and anything outside 100–599 all have to land on `"unknown"`, and the only way to keep them out is to state the floor as well as the ceiling. Note also that `200 <= code < 300` is legal Python and means what it looks like it means; most languages make you write it as two comparisons joined by "and".

---

### `should_retry`

This one needs no loop and no `if` statement at all. The docstring describes two conditions that must both hold, and Python's comparison operators already produce `True` and `False`, so you can hand back the answer as a single expression:

```python
return (code == 429 or code >= 500) and attempt < max_attempts - 1
```

The left half is "is this the kind of failure that might fix itself", the right half is "do I have a try left". Getting the `- 1` right is the fiddly bit: attempts are numbered from zero, so with `max_attempts` of 3 the last permitted try is number 2, and on that attempt there is nothing further to schedule. The tests check `should_retry(500, 2)` is `False` for exactly this reason.

The tests use `is True` and `is False` rather than `==`, which insists on the real boolean objects rather than anything merely truthy. The expression above already produces real booleans, so you are fine — but this is why returning something like `1` or a non-empty list would fail even though it would "work" in an `if`.

---

### `first_match`

Loop over the records and return the instant one matches. `return` inside a loop leaves both the loop and the function in a single move, which is why you never need a flag variable or a `break` followed by a check:

```python
for record in records:
    if record.get(field) == value:
        return record
return None
```

`.get(field)` is what makes the missing-field case behave. If a record has no such key, `.get` quietly hands back `None`, which will not equal the value you are looking for, so that record is skipped instead of blowing up — whereas `record[field]` would raise a `KeyError` and take the whole function down. The final `return None` is what runs when the loop finishes having found nothing; Python would return `None` on its own if you omitted it, but writing it makes the intent visible to whoever reads this next.

---

### `find_index_of_drop`

Here you genuinely want positions, not values, because the position is the answer. Start the count at 1 rather than 0 so that every index you look at is guaranteed to have something before it:

```python
for i in range(1, len(values)):
    if values[i] < values[i - 1]:
        return i
return None
```

Starting at 1 is doing real work: at `i` of 0 there is no `i - 1` to compare against, and in Python `values[-1]` does not error — it silently wraps round to the *last* element of the list, so you would be comparing the first value against the last one and getting a nonsense answer with no complaint. Beginning at 1 sidesteps that entirely.

The comparison is `<` and not `<=`, which is what makes `[2, 2, 1]` return 2 rather than 1: two equal values in a row are flat, not a drop. And the short inputs need no special handling, because for a one-element list `range(1, 1)` is empty and for an empty list `range(1, 0)` is empty too, so the loop body never runs and you fall through to `return None`.

---

### `fizz_report`

The loop bounds come straight from the "1 to n inclusive" wording. `range` excludes its stop value, so you need to go one past `n`:

```python
for i in range(1, n + 1):
    ...
```

This also handles `fizz_report(0)` by itself — `range(1, 1)` is empty, the loop never runs, and you return the empty list you started with.

Inside, order the conditions with the most specific one first. A number divisible by both 3 and 5 is also divisible by 3, so if the `% 3` test comes first it will grab 15 and the `"both"` branch will never execute for any input at all. Test for both-at-once before either individual case, either with `i % 15 == 0` or with `i % 3 == 0 and i % 5 == 0` — they are the same test written two ways.

One last detail that is easy to miss: the unlabelled numbers go in as strings, so it is `str(i)` that gets appended, not `i`. The tests compare against `["1", "2", "low", ...]` and a bare integer will not match.

---

### `collect_pages`

The whole function is one `while` loop with the page number as its counter, the cap in the loop condition, and the empty page as a `break`:

```python
out = []
page = 1
while page <= max_pages:
    batch = fetch_page(page)
    if not batch:
        break
    out.extend(batch)
    page += 1
return out
```

Three things are load-bearing there. `while page <= max_pages` is the hard cap, and putting it in the loop header means you cannot forget it. `if not batch: break` is the stop signal from the server — an empty list is falsy, so `not batch` is true exactly when the page came back with nothing. And it is `extend`, not `append`: `extend` adds each record from the batch individually, giving you the flat list the docstring asks for, whereas `append` would add the whole page as a single item and leave you holding a list of pages.

**About the extra call, because it looks like a bug and is not.** One test asserts that with two pages of data, the page numbers you request are exactly `[1, 2, 3]`. Page 3 does not exist, and you asked for it anyway. That is correct. There is no way to know a page is the last one just by looking at it — a full page might be the final page, or there might be a hundred more. The only thing that tells you the source is exhausted is asking for the next one and getting nothing back. So you fetch one page past the end, see it is empty, and stop. Real APIs work exactly this way, which is why the test pins the behaviour down: it is checking both that you *do* make that call and that you make no more after it. Watch also the empty-source test, where a fetcher with no pages at all should produce exactly one call, to page 1.

---

### `collect_until`

The same loop with one more exit. After you have extended `out` with the current batch, check whether you have reached the target and break if you have:

```python
if len(out) >= target_count:
    break
```

Place it after the `extend`, because the count you are testing has to include the page you just took. Placing it at the top of the loop instead would test a stale number and fetch one page more than necessary — which is what the test catches when it asserts that pages `[1, 2]` were fetched and not `[1, 2, 3]`.

Use `>=` rather than `==`. Pages arrive whole, so your total jumps in steps of however many records a page holds and will very often skip straight past the exact target — three records a page against a target of five gets you 3, then 6, and never touches 5. An `==` test would miss it and keep looping until the source ran dry. Once you break, return what you have collected without trimming; the extra record or two is the caller's to discard.
