# Unit 07 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `names_of`

This is the whole comprehension in one line, so let me give you the shape and spend the words on how to read it rather than on how to derive it.

```python
[r["name"] for r in records]
```

Read it in that order as an English sentence: *"give me `r["name"]`, for each `r` in `records`."* The front slot holds what you want out, the `for` clause says where it comes from. Square brackets on the outside mean the result is a list. If you squint it is `SELECT name FROM records` with the clauses swapped round, and that reordering is the only thing about comprehensions that feels wrong for the first day.

Square brackets are safe here because every record in this data has a name. Elsewhere in the file you will want `.get()` instead — if a single record out of five hundred is missing the key, `r["name"]` raises `KeyError` and you lose the whole result, including the 499 that were fine, because a comprehension either produces a complete list or produces an exception.

---

### `active_python_repos`

You want a filter, which means an `if` after the `for` clause and no `else` anywhere. Two conditions have to hold at once, so join them with `and` inside that single `if`.

```python
[r["name"] for r in records if r.get("language") == "Python" and not r.get("archived")]
```

The two conditions are worth taking separately. `r.get("language") == "Python"` handles all three cases you care about without a branch: it is `True` for the Python repos, `False` for `"HTML"`, and `False` both when the key is missing and when it is present holding `None` — because `.get()` returns `None` in both of those situations, and asking whether `None == "Python"` is legal and simply answers no. That is why the messy records exclude themselves.

`not r.get("archived")` reads as "not archived". `.get("archived")` gives you `True`, `False`, or `None` if the key were absent, and `not` turns all of the falsy ones into `True`, so a repo with no `archived` key counts as active. That is the sensible default and it needs no extra handling.

---

### `stars_by_name`

A dictionary comprehension: curly braces, and the front slot holds a `key: value` pair separated by a colon rather than a single expression.

```python
{r["name"]: r["stars"] for r in records}
```

The colon is the entire difference between this and a set comprehension, which matters in the very next function. Everything after the `for` works identically to a list comprehension — same loop, same optional filter — only the shape of what comes out has changed.

---

### `distinct_languages`

Two steps, and it is easier if you write them as two steps first and combine them afterwards. Collect the languages into a set, which drops duplicates for you, filtering out the empty ones as you go. Then sort the set into a list.

```python
sorted({r["language"] for r in records if ...})
```

Curly braces with no colon make a set, so `"Python"` appearing on five records still lands once. The filter in the `if` slot has to reject both the missing-key case and the present-but-`None` case; `r.get("language")` returns `None` for both, and `None` is falsy, so a simple truthiness test covers them together.

`sorted()` around the outside is doing two jobs, not one. It puts the values in alphabetical order, and it converts the set into a list — sets have no order at all, so without it the same correct answer would come back arranged differently between runs and the test could not compare it against a fixed expectation.

---

### `total_forks`

A generator expression handed straight to `sum`. No square brackets inside the parentheses — that is the whole point.

```python
sum(r.get("forks", 0) for r in records)
```

If you wrote `sum([...])` with brackets, Python would build the entire list of fork counts in memory, add it up, and throw the list away. Without them it computes one value at a time and never holds more than one, which costs nothing here and matters enormously at fifty thousand rows. You do not need a second pair of parentheses around the generator because it is `sum`'s only argument.

The `0` default in `.get("forks", 0)` is not cosmetic. One repo in `REPOS` has no `forks` key, and without the default you would hand `sum` a `None`, which it cannot add to anything. `sum` of nothing at all is already `0`, so the empty-input case needs no code from you.

---

### `rank_by_stars`

Sort the records first, then pull out the names, then apply the limit. Three separate lines are clearer here than one dense one, and an interviewer reading over your shoulder will prefer them too.

```python
ranked = sorted(records, key=lambda r: (-r.get("stars", 0), r["name"]))
names = [r["name"] for r in ranked]
return names if limit is None else names[:limit]
```

The key returns a two-element tuple, and Python compares tuples left to right — the first element decides, and only when two are equal does it look at the second. So the star count is the primary ordering and the name is the tiebreaker, exactly like the two columns in an `ORDER BY`.

The minus sign is how you get one column descending while the other stays ascending. `reverse=True` would flip the whole tuple, including the name tiebreaker, which would give you `["b", "a"]` on equal scores instead of the `["a", "b"]` the test wants. Negating turns the biggest star count into the smallest tag, so ascending order on the tags is descending order on the stars, and the un-negated name in the second slot sorts normally. Note that this trick only works on numbers — there is no `-"flask"` — so for a text column descending you would sort twice and lean on stability instead.

That last line could just be `return names[:limit]`. Slicing with a bound of `None` returns the whole list, because Python treats a `None` bound and an omitted bound identically. Both forms are correct; the explicit one says what you meant.

---

### `sort_with_missing_last`

This one deserves a named function rather than a `lambda`, because it needs two steps and a lambda can only hold one expression. Define it inside `sort_with_missing_last` so it can see the `field` parameter, then pass it to `sorted`.

```python
def key(record):
    value = record.get(field)
    return (value is None, value if value is not None else 0)

return sorted(records, key=key)
```

The first element of the tuple is a boolean, and booleans sort as though `False` were `0` and `True` were `1`. So every record with a real value gets a tag beginning `False` and lands in the front block, every missing one gets `True` and lands at the back. That single boolean carves the data into "present" and "missing" before any number is compared, which is how you say "nulls last" in a language that has no `NULLS LAST` clause.

The second element only ever matters inside the front block, where the booleans tie and Python moves on to compare the actual values.

**Now the part that is worth the most in this unit.** You will find this shorter version in a lot of places, and it is broken on this task's own test data:

```python
key=lambda r: (r.get(field) is None, r.get(field, 0))     # DO NOT USE
```

The test passes `[{"n": 3}, {"n": None}, {"n": 1}, {}]`, which contains both flavours of missing: one record where the key is present holding `None`, and one where the key is absent entirely. A `.get` default only fires when the key is *absent*. So `{"n": None}` produces the tag `(True, None)` while `{}` produces `(True, 0)`. Both are in the missing block, so their first elements tie, so Python compares `None` against `0` — and raises the exact `TypeError` the boolean was supposed to prevent. It works right up until your data contains both kinds of missing, which real data does.

The fix in the scaffolding above normalizes on `is None` rather than on the `.get` default. Read the value once, then decide from the value itself. Now both flavours of missing produce the identical tag `(True, 0)`, they compare equal, and Python's stable sort leaves them in their original input order — which is what the expected result shows, `{"n": None}` before `{}`.

One last requirement: `sorted()` returns a new list and leaves the caller's alone, which one of the tests checks explicitly. The `.sort()` method would rearrange the input in place and return `None`.

---

### `group_names_by_language`

An ordinary loop, not a comprehension. Grouping accumulates several records into one growing list, and a comprehension can only produce one output item per input item, so this is the one place in the file where the loop is the right answer rather than a compromise.

```python
out = {}
for r in records:
    out.setdefault(r.get("language"), []).append(r["name"])
return out
```

`setdefault` does lookup-or-create in a single step: if the language is already a key it hands you back the list that is there, and if it is not, it stores a fresh empty list under that key and hands you *that*. Either way you get a list back and can append to it immediately, with no "have I seen this language before?" check.

Two details fall out for free. Appending in input order means each group's names stay in their original order, which the spec asks for. And `r.get("language")` returns `None` for the `meta` repo, which becomes the dictionary key `None` — `None` is a perfectly ordinary dictionary key, so those records group together rather than being dropped.

---

### `stars_summary`

Handle the empty input before you do anything else. It is not an afterthought here; two of the four values you have to compute would blow up on it.

```python
if not records:
    return {"count": 0, "total": 0, "mean": None, "max_name": None}
```

That guard is what saves you from both `max()` raising `ValueError` on an empty collection and from dividing by a count of zero to get the mean. If you would rather not guard, `max(records, key=..., default=None)` handles the first problem and a conditional expression handles the second, but the early return is less to get wrong.

With that out of the way, `count` is `len(records)`, `total` is the same `sum(... for ...)` pattern as `total_forks`, and the mean is `round(total / count, 2)` for the two decimal places the test expects.

For `max_name`, the tie rule is "name ascending", which is the same requirement `rank_by_stars` already solved. Rather than reasoning about `max` and ties from scratch, sort with the same key and take element `[0]`:

```python
top = sorted(records, key=lambda r: (-r.get("stars", 0), r["name"]))[0]
```

That works because the sort has already put the highest star count first and broken any tie alphabetically, so the first element is the answer by construction. It is slower than `max` on a large list and completely fine here.

---

### `label_sizes`

A ternary in the front slot of the comprehension, producing a tuple for each record.

```python
[(r["name"], "big" if r.get("stars", 0) >= threshold else "small") for r in records]
```

The inner parentheses build the two-item tuple that each item of the result is. Inside them, `"big" if ... else "small"` is the ternary: it sits where a value is expected, so it must produce one for every record, which is why the `else` is mandatory and why the output is always the same length as the input.

Compare that with `active_python_repos`, where the `if` sat after the `for` with no `else` and dropped records. Same file, same data, opposite constructions — and the position of the `if` relative to the `for` is the entire difference between them.

`.get("stars", 0)` covers the record with no stars key, and `>=` rather than `>` is what makes a repo sitting exactly on the threshold count as big, which one of the tests checks directly.
