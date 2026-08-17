# Unit 03 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `dedupe_preserving_order`

The trick is that you need two containers at once, each doing the job it is good at. A set answers "have I already seen this?" instantly no matter how big it grows, but it has no order. A list keeps order but is slow to search. So use a set purely as your memory and a list purely as your answer:

```python
seen = set()
out = []
for x in items:
    if x not in seen:
        ...
```

Inside that `if`, you have to do two things, and forgetting either one is the common mistake: record `x` in `seen` so you recognise it next time, and append `x` to `out` so it appears in the result. Then return `out`. Because you only ever build a new list and never touch `items`, the caller's list comes back unharmed — which one of the tests checks.

---

### `chunk`

Deal with the nonsense case first. If `size` is zero or negative there is no sensible way to cut the list, and a loop that advances by zero would run forever, so return `[]` immediately and stop thinking about it.

For the real work, you do not need to count items yourself. `range` takes a third argument, a step, so you can generate the starting position of every chunk directly:

```python
for i in range(0, len(items), size):
    out.append(items[i:i + size])
```

This works because of a property of slicing that unit 02 mentioned: a slice never complains about running past the end of the list, it just stops there. So on the last chunk, `items[4:6]` on a five-item list quietly gives you the single leftover item instead of raising an error. That is why the short final chunk needs no special handling.

---

### `flatten`

Two loops, one inside the other: walk the outer list to get each inner list, then walk that inner list to get each item, appending as you go.

There is a one-loop version that reads better, and it is worth writing because it forces you to get `append` and `extend` straight:

```python
for inner in nested:
    out.extend(inner)
```

`extend` takes the collection you give it and adds each of its items separately, which is exactly flattening. `append` would add the whole inner list as a single item and leave you with the nesting you started with. An empty inner list contributes nothing and needs no check.

---

### `min_max`

Guard the empty case before you do anything else, then let Python's built-ins do the actual work:

```python
if not numbers:
    return None
return (min(numbers), max(numbers))
```

The guard has to come first because `min([])` raises an error rather than returning anything. And note that `return (min(...), max(...))` is how you return two things — the parentheses build a tuple, and the caller can split it apart with `low, high = min_max(xs)`.

---

### `compare_id_sets`

Convert both inputs to sets first. That is one line each and it buys you the whole answer, because sets support the comparison operators directly:

```python
left_set = set(left)
right_set = set(right)
only_left = left_set - right_set
```

Subtraction means "in the left one, not in the right one", so flip the operands for the other direction. The `&` operator gives you the intersection — the items in both. Then wrap each of the three results in `sorted(...)`, which turns a set into a list in ascending order, and return them as a tuple in the order the docstring specifies: only-left, only-right, both.

The `sorted` step is not decoration. Sets have no order, so without it the same correct answer would print differently on different runs and the test could not compare against a fixed expected value.

---

### `running_total`

Keep one variable outside the loop that survives from one item to the next. That is the accumulator:

```python
total = 0
for n in numbers:
    total += n
    out.append(total)
```

The order of those two lines inside the loop matters. Add first, then append, so what lands in the output is the total *including* the current number — which is what the examples show. Appending `n` instead of `total` is the mistake to watch for, and it produces a copy of the input rather than an error, so nothing will warn you.

---

### `top_n`

Sort with a key function that returns a tuple. Python compares tuples element by element, so a two-element key gives you a primary sort and a tiebreaker in a single pass:

```python
ranked = sorted(pairs, key=lambda p: (-p[1], p[0]))
```

`p` is one `(label, score)` tuple, so `p[1]` is the score and `p[0]` is the label. Negating the score makes larger scores sort earlier, since ascending order on negative numbers is descending order on the originals. The label stays un-negated, so equal scores fall back to alphabetical order — which is the tie rule the docstring asks for.

Then take the first `n` with a slice, `ranked[:n]`, and loop over that appending only the label from each pair. The slice handles `n` larger than the list for free, because slicing never runs past the end.

---

### `pair_with_next`

Loop over positions rather than items, because you need to reach one place ahead:

```python
for i in range(len(items) - 1):
    out.append((items[i], items[i + 1]))
```

Stopping one short of the end is what makes `items[i + 1]` always valid. It also handles the short inputs by itself: for a one-item list `range(0)` is empty and for an empty list `range(-1)` is empty too, so the loop body simply never runs and you return `[]` without writing any special case.

---

### `merge_sorted`

Two counters, `i` for `a` and `j` for `b`, each marking how far into its list you have got. While both lists still have something left, compare the two front items and take the smaller:

```
i = j = 0
while i < len(a) and j < len(b):
    take the smaller, advance that counter
then append whatever remains of a, then of b
```

The loop stops as soon as *either* list is used up, which means one of them still has items in it. Those items are already sorted and already larger than everything you have taken, so you can append the whole remainder in one go: `out.extend(a[i:])` then `out.extend(b[j:])`. Only one of those two lines will actually add anything, and slicing from a position at or past the end gives an empty list rather than an error, so neither needs a check.

Use `<=` rather than `<` when you compare, so that when the two front items are equal you take the one from `a`. That is what keeps the merge stable, and it is the detail an interviewer is most likely to ask you about.
