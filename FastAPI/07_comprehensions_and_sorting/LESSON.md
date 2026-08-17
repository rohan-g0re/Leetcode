# 07 — Comprehensions and Sorting

*This is the unit where your Python starts looking like Python. It's about doing something to a whole collection at once — reshaping it, filtering it, ordering it — in a single line a reader can take in at a glance. About twenty-five minutes. You need units 03 and 04 solid first; if `.get()` isn't reflexive yet, go back.*

*Your SQL background is worth more here than anywhere else in the course. A comprehension is very nearly a `SELECT ... WHERE`, and sorting by a key is very nearly an `ORDER BY`. I'll make those comparisons explicitly, because they aren't analogies I'm stretching — they're the same idea in different syntax.*

---

## 1. What you are actually learning here

By the end of unit 04 you had the target shape: a **list of flat dictionaries**, one dictionary per record, keys as column names. That's your result set, and this unit is everything you do to one once you have it. There are really only five moves, and you know all five from SQL. Pick out some columns. Drop the rows you don't want. Compute a total. Get the distinct values of something. Put it in order. This unit gives you one line of Python for each — which matters in an interview, where six lines of loop appending one item at a time say "I can do this" and one line saying the same thing says "I do this every day."

There's a quieter reason too. A comprehension always builds a **new** collection and never modifies the one you started from. Unit 01 taught you that a variable is a name pointing at an object rather than a box holding one, and units 03 and 04 showed you the bugs that fall out of that — you change a list through one name and it changes under another. Comprehensions sidestep that whole family of bugs by construction: nothing is mutated because nothing is touched.

---

## 2. The list comprehension

Here is a loop that builds a list, and the same thing as a comprehension.

```python
squares = []
for n in nums:
    squares.append(n * n)

squares = [n * n for n in nums]
```

The second is a **list comprehension** — square brackets holding an expression, then a `for` clause. An **expression** is any piece of code that produces a value: `n * n`, `r["name"]`, `len(x)`. That's the only thing allowed in the front slot; no assignment, no `print`, no bare `if`. The restriction is deliberate, and it's what keeps a comprehension to one readable thought.

Read it left to right as a sentence: *"give me `n * n`, for each `n` in `nums`."* That order feels backwards for about a day and then stops feeling like anything, because it's how you'd say it out loud. Squint and it's SQL with the clauses reversed: `SELECT n * n FROM nums`. Applied to a list of dictionaries, the shape is always the same:

```python
names = [r["name"] for r in records]
logins = [r.get("login") for r in users]
```

That's your `SELECT one_column FROM records`. Note `.get()` on the second line — unit 04's lesson doing its work inside a comprehension. If one record out of five hundred lacks `login`, square brackets raise a `KeyError` and you lose the whole result including the 499 that were fine. Inside a comprehension there is no partial result to salvage; the line either produces a list or produces an exception.

**One practitioner's detail.** The loop variable is private to the comprehension — if `n` existed before the line, it still holds its old value afterwards. A plain `for` loop isn't like that; `n` survives it holding whatever it saw last. So a comprehension is safe to drop into existing code without inventing `n2` to avoid a collision.

**Mental model: a comprehension is a sentence with three slots — what I want, where it comes from, which ones count.** The rest of this lesson is filling in that third slot properly.

---

## 3. Filter or choice — position tells you which

**This is the section that matters, and it's the one thing about comprehensions that genuinely confuses people.** An `if` can go in two places, they do completely different jobs, and the only thing distinguishing them is where they sit relative to the `for`.

An `if` **after** the `for` is a filter. It decides which items get into the result at all.

```python
[n for n in nums if n > 0]
[r["login"] for r in users if r.get("followers", 0) > 100]
```

That is a `WHERE` clause, exactly — the second line is `SELECT login FROM users WHERE followers > 100` — and like a `WHERE` clause it makes the output *shorter* than the input. Rejected items are simply never produced.

An `if/else` **before** the `for` is a choice. Every item survives; the `if` only picks which of two values gets produced for it.

```python
["high" if n > 50 else "low" for n in nums]
```

That's a **ternary expression** — "ternary" meaning three parts: a value, a condition, another value. Read it as *"`high` if `n > 50`, otherwise `low`."* It's Python's `CASE WHEN ... THEN ... ELSE ... END`, and like `CASE` it produces something for every row, so the output is always exactly as long as `nums`.

- `[expr for x in xs if cond]` — filter. Drops items. Output shorter.
- `[a if cond else b for x in xs]` — ternary. Keeps everything, chooses a value. Same length.

The reliable way to remember it: a ternary *must* have an `else`, because an expression has to produce something for every item and there's no such thing as "produce nothing." A filter *must not* have one, because there's nowhere for a rejected item to go. When you can't tell which a line is, look for the `else`. Both in one line is legal and I'd rather you didn't; `[a if c1 else b for x in xs if c2]` reads like a puzzle.

**Where this hits your task.** `active_python_repos` wants a filter — non-archived Python repos only, output shorter than input. `label_sizes` wants a ternary — every repo gets a `"big"` or `"small"` and nothing is dropped. Same data, opposite constructions.

**One practitioner's detail, and it's a small gift.** In the filter version you need no special branch for missing data. `r.get("language") == "Python"` is `False` when the key is missing and `False` when it's present holding `None`, and neither raises — comparing `None` to a string with `==` is a legal question with a boring answer. The messy records exclude themselves. Section 11 is where `None` stops being polite.

---

## 4. Two `for` clauses, for flattening

A comprehension can have more than one `for`, and the case you'll actually meet is flattening: you fetched five pages from a paginated API, each page is a list of records, and you want one list.

```python
records = [record for page in pages for record in page]
```

Read the `for` clauses in the same order you'd write nested loops — outer first, inner second. The outer walks the pages, the inner walks the records inside the current page, and the front expression is what gets collected. It's the `for` order that trips people, so lean on that rule. Two levels is the practical limit.

---

## 5. Dictionary and set comprehensions

Same syntax, different brackets, and both are things you already wanted in unit 04.

```python
{r["id"]: r for r in records}                    # lookup table, keyed by id
{k: v for k, v in d.items() if v is not None}    # drop the empty fields
{r["language"] for r in records}                 # the distinct languages
```

The first two are **dictionary comprehensions** — curly braces with a `key: value` pair at the front. The first is unit 04's lookup table, which is what a join looks like underneath; the second cleans a record by dropping null fields, which is what you do before writing rows to a CSV.

The third is a **set comprehension** — curly braces with no colon. A set is unit 03's unordered collection of unique values, so that's your `SELECT DISTINCT`. The brackets are the only difference: `{...}` with a colon is a dictionary, without one is a set. Worth saying once, because they look identical at a glance.

Sets have no order, so when you want sorted distinct values — and you usually do — wrap it:

```python
sorted({r["language"] for r in records if r.get("language")})
```

That's `SELECT DISTINCT language FROM records WHERE language IS NOT NULL ORDER BY language`, and it's close to what `distinct_languages` asks of you.

---

## 6. Generator expressions

Swap square brackets for parentheses and you get a **generator expression**: values computed one at a time, on demand, nothing stored.

```python
total = sum(n * n for n in nums)
any(r["status"] == "error" for r in rows)
max(r["score"] for r in rows)
```

The parentheses are usually invisible, because when a generator expression is a function's only argument you may drop the extra pair — those three lines are complete as written.

**Why bother.** `sum([n * n for n in nums])` builds the entire list of squares, adds it up, then throws the list away. The generator version never builds it: `sum` pulls one value, adds it, asks for the next. On a hundred records nobody can measure the difference; on fifty thousand rows it's the difference between a program and a memory problem. Rule of thumb: **if the result goes straight into `sum`, `any`, `all`, `max`, or `min`, use a generator**; if you need the list itself, use a list.

**The catch, and this is the bug everyone hits once: a generator is one-shot.**

```python
g = (n for n in [1, 2, 3])
sum(g)     # 6
sum(g)     # 0
```

The second `sum` doesn't fail and doesn't warn you. It quietly returns zero, because the generator has already been walked to the end. If a total comes out as `0` when it shouldn't, check this first.

**Mental model: a list comprehension is a photograph, a generator is a live feed. The photograph is still there tomorrow. The feed plays once.**

`total_forks` asks for a generator specifically — `sum(r.get("forks", 0) for r in records)`. The `.get` default matters, because one repo in `REPOS` has no `forks` key and `sum` cannot add `None` to anything.

---

## 7. When not to use a comprehension

Comprehensions are satisfying enough that the failure mode is overuse, and I want to be direct because this is a readability problem, not a style preference.

Don't use one when the body needs more than one step — if you'd have to compute an intermediate value or handle an error, write the loop. Don't use one for a side effect: if you're calling `print()` and discarding the result, you've built a list of `None` for no reason and confused your reader about what the line is for. And don't use one when it stops fitting comfortably on a line.

```python
[expensive(x) for x in xs if check(x) and other(x) or fallback(x)]
```

That is not clever, it's a future bug in a costume, and whoever modifies it — probably you, in three weeks — has to hold four things in their head to change one. In an interview the reviewer is reading it live off your screen, and clarity wins the point where compression doesn't. One comprehension does one thing; if it's doing two, it's two lines or a loop.

---

## 8. Sorting: two functions, one property that makes it all work

```python
sorted(xs)                    # returns a NEW sorted list
sorted(xs, reverse=True)      # descending
xs.sort()                     # sorts xs in place, returns None
```

The difference is unit 01's mutation question again. `sorted()` leaves your input alone and hands back a new list. `.sort()` rearranges the list you have and returns `None` — so `result = xs.sort()` sets `result` to `None`, the mistake everyone makes exactly once. Prefer `sorted()`; new data over modified data is the same instinct comprehensions gave you, and `sort_with_missing_last` tests that you didn't modify the input.

The property everything below depends on: **Python's sort is stable.** When two items compare equal they come out in the order they went in. That's why tie-breaking rules in these tasks are well defined rather than luck, and why sorting twice in a row gives a compound ordering — the second sort preserves the first one's work wherever it has no opinion.

---

## 9. `key=` — sorting by something you compute

By default `sorted` compares the items themselves, which is useless when your items are dictionaries. **`key=` takes a function that is applied to each element, and the results of that function are what actually get sorted.**

```python
sorted(words, key=len)                            # by length
sorted(names, key=str.lower)                      # case-insensitive
sorted(records, key=lambda r: r["score"])         # by a field
sorted(records, key=lambda r: r["score"], reverse=True)
```

**Mental model: `key` is a translator. Python never sorts your records — it hangs a tag on each one, sorts the tags, and brings the records along for the ride.** Everything hard about sorting real data gets easy once you ask "what tag do I want on each record?" instead of "how do I make sorting do this?"

That `lambda` needs defining. A **lambda** is an **anonymous function** — no name, written inline, exactly one expression, whose value it returns. `lambda r: r["score"]` behaves identically to `def whatever(r): return r["score"]`. It cannot contain statements, assignments, or multiple lines, and its only real job is being handed to `key=` without the ceremony of a `def` three lines above. If yours is getting long, write the named function — not a defeat, usually the better code.

**One practitioner's detail.** `key` is called exactly **once per element**, not once per comparison: Python computes all the tags up front, sorts those, then reassembles. So an expensive key function is still cheap, and you never need to optimize one.

---

## 10. Sorting by more than one thing

Return a **tuple** from your key. Tuples compare element by element, left to right — the first elements decide, and only on a tie does Python look at the second.

```python
sorted(rows, key=lambda r: (r["dept"], r["name"]))      # dept asc, then name asc
```

That's `ORDER BY dept, name`, and the comma in the tuple is doing the same job as the comma in `ORDER BY`.

The awkward case is one column descending and another ascending, because `reverse=True` flips *everything*, tiebreaker included. Negate the number instead:

```python
sorted(rows, key=lambda r: (-r["score"], r["name"]))    # score DESC, then name ASC
```

Negating turns the biggest score into the smallest tag, so ascending order on tags is descending order on scores, while the name in the second slot sorts normally. That's `ORDER BY score DESC, name ASC`, and it's exactly the line `rank_by_stars` needs.

**One practitioner's detail: negation only works for numbers.** There is no `-"flask"`. For a string field descending with an ascending tiebreaker, do two separate sorts and lean on stability — sort by the *least* significant key first, then by the most significant with `reverse=True`. That's the general escape hatch when one tuple key can't express what you want.

---

## 11. Sorting real data that contains `None`

**This is the differentiator.** Everything above assumes the sort field is present and filled in on every record. Real API data isn't like that — the thread running through units 01 and 04 — and it lands harder here than anywhere else.

The first failure is easy, and you know the fix:

```python
sorted(records, key=lambda r: r["score"])          # KeyError on the first record without it
sorted(records, key=lambda r: r.get("score", 0))   # missing sorts as zero
```

The second is nastier, because `None` is not something Python knows how to order:

```python
sorted([1, None])
# TypeError: '<' not supported between instances of 'NoneType' and 'int'
```

Python is right to refuse. There's no correct answer to "is nothing smaller than one?" — it depends on what you're doing, so you have to say. You say it by putting a second field in *front* of your sort key: a boolean for whether the value is missing.

```python
key=lambda r: (r.get("score") is None, r.get("score", 0))
```

`False` sorts before `True`, because underneath `False` is `0` and `True` is `1` — unit 01's quirk turning out to be load-bearing. Records that have a score get a tag starting `False` and land in the front block; missing ones get `True` and land at the back. Only inside the front block does the number matter. **Mental model: a boolean is a sorting column with two values, and putting one first is how you carve the data into "present" and "missing" before sorting anything.**

That's the version you'll see everywhere, and **it has a bug the task will catch you with.** Remember unit 04: a `.get()` default only fires when the key is *absent*. If the key is present holding `None`, `.get("score", 0)` hands back `None`. So on data like `[{"n": None}, {}]` the tags are `(True, None)` and `(True, 0)`, both in the missing block, and comparing them means comparing `None` with `0` — the exact `TypeError` you were avoiding. It works until your data contains both flavours of missing.

Normalize on `is None` rather than on the `.get` default, which takes two steps:

```python
def missing_last(record):
    value = record.get("score")
    return (value is None, 0 if value is None else value)
```

Now everything missing gets the identical tag `(True, 0)`, they all compare equal, and stability keeps them in their original order — precisely what `sort_with_missing_last` wants. This is a lambda that grew up into a `def`, as section 9 said it should.

Saying this out loud in an interview — *"I'm putting nulls last deliberately, and keying off `is None` rather than a `.get` default because a present-but-null field slips past the default"* — is worth more than the code.

---

## 12. `min` and `max`, and the empty case

Both take the same `key=`, and this distinction catches people under pressure:

```python
max(records, key=lambda r: r["score"])    # the whole RECORD with the top score
max(r["score"] for r in records)          # just the NUMBER
```

Usually you want the record, because "flask has the most" beats "the most is 66000." Same point unit 04 made at the end of its section 10, now with the syntax explained.

The trap is empty input: `max([])` raises `ValueError`, which happens the first time a filter matches nothing. Pass a default.

```python
max(records, key=lambda r: r["stars"], default=None)
```

`stars_summary` needs this *and* unit 01's divide-by-zero guard, since a mean is `total / count` and `count` is zero on empty input. The task wants `None` for the mean there, and `round(value, 2)` for two decimal places otherwise.

---

## 13. Three small things the task needs

Grouping is not a comprehension. For `{language: [names...]}` the shape is unit 04's `setdefault` idiom in an ordinary loop — `groups.setdefault(r.get("language"), []).append(r["name"])`. A comprehension can't accumulate into a growing list, and forcing it is section 7 in action. Note that `None` is a perfectly good dictionary key, which is why the expected result has a `None` group rather than dropping those records.

Slicing takes `None` gracefully. `rank_by_stars` has a `limit` that may be `None` meaning "all," and you need no branch for it: `ordered[:limit]` returns the whole list when `limit` is `None`, because an omitted slice bound and a `None` bound are the same thing to Python.

And sorting and slicing compose — "top three by stars" is sort everything, then take three, which is fine at this scale. At a million records you'd reach for `heapq.nlargest`, which is in the next section.

---

## 14. What I have deliberately left out

None of these are needed for the task, but you'll want each within a month of writing real data code, and looking them up yourself is the habit this course is actually building. Two minutes at the interactive prompt with `help()` beats twenty minutes of guessing.

Find out what `operator.itemgetter("score")` does and why people prefer it to `lambda r: r["score"]`. Look at `sorted(..., key=str.casefold)` and how it differs from `str.lower` on non-English text. Read up on `heapq.nlargest(3, records, key=...)`, which gets you the top three without sorting the other nine hundred and ninety-seven. Look at `itertools.groupby`, paying attention to the part where it only groups *adjacent* equal items — it silently gives wrong groups unless you sort first, which is a real trap. And try `enumerate` inside a comprehension when you need the index alongside the item, plus the walrus operator `:=`, which lets a comprehension compute something once and use it in both the filter and the output.

---

## 15. Check yourself

Answer these before opening the task. If one isn't obvious, reread the section it came from — cheaper than getting stuck later and not knowing why.

1. Rewrite `out = []` / `for x in xs:` / `if x > 0:` / `out.append(x * 2)` as a comprehension.
2. Where does the `if` go for filtering, and where for choosing a value?
3. Why does `sum(g)` return `0` the second time you call it on a generator `g`?
4. Sort records by score descending, then name ascending, in one call.
5. What breaks when you sort records where some have `None` for the sort field?
6. Does `max(records, key=lambda r: r["n"])` give you a record or a number?
7. Why is `r.get("score", 0)` not enough to make a missing-values-last sort safe?

*(Answers: 1. `[x * 2 for x in xs if x > 0]`. 2. filtering: after the `for`, with no `else`; choosing: before the `for`, and it must have an `else`. 3. generators are one-shot — the first `sum` walked it to the end, and there's no error to warn you. 4. `sorted(records, key=lambda r: (-r["score"], r["name"]))`. 5. `TypeError` — `None` can't be compared with numbers or strings, so Python refuses rather than guessing. 6. the record. 7. because a `.get` default only applies when the key is absent; a key present holding `None` returns `None` and crashes the comparison anyway — normalize on `is None` instead.)*

---

*Three things to carry out of this unit. A comprehension is a `SELECT` with the clauses reordered, and the position of the `if` is the entire difference between a `WHERE` that drops rows and a `CASE` that labels them. `key=` is a translator that hangs a tag on each record, which makes multi-column ordering just a tuple and descending-plus-ascending just a minus sign. And real data has holes, so every sort against an API response needs an explicit decision about where the nulls go — that decision is a boolean in the first slot of your key, and getting it right for both missing keys and present-nulls is what separates code that works from code that works on your test data. Unit 08 is error handling: this unit was about preventing the crash, that one is about catching it.*

*Now open [`task.py`](task.py).*
