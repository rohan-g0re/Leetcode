# 03 — Collections: Lists, Tuples, and Sets

*About fifteen minutes of reading, then the task. Units 01 and 02 gave you individual values; this lesson is about holding many of them at once. Read straight through — everything is defined as it appears.*

---

## 1. The shape of every API response

Go back to that JSON from unit 01 and imagine the realistic version. You almost never ask an API for one thing. You ask for a user's repositories, or a search result, or last month's transactions — and what comes back looks like this:

```
[ {...}, {...}, {...}, {...} ]
```

Square brackets, holding many similar items. In JSON that's called an **array**. In Python, it becomes a **list**.

If you've written SQL, you already have the right instinct for this: a list of records is a result set, and each item in it is a row. Everything you'd naturally want to do — count them, filter them, sort them, pull one column out — has a direct equivalent here, and by unit 07 you'll be writing them almost as compactly.

This lesson covers three containers. **Lists** are the one you'll use constantly. **Tuples** are a small variant that matters for two specific reasons. **Sets** are a specialist tool that turns certain awkward questions into one-liners. Of the three, lists are load-bearing — if you only get one solid, make it that.

---

## 2. Lists

**What it is.** A list holds items in order, and you can change it after you've made it. You write one with square brackets:

```python
xs = [10, 20, 30]
xs = []              # an empty list, ready to be filled
```

It can hold anything, including a mix of types, though in practice yours will be uniform — five hundred records that all have the same shape.

**Getting things out.** Same rules as strings in unit 02, which is not a coincidence: both are sequences, so both use the same syntax.

```python
xs[0]       # 10        — positions start at zero
xs[-1]      # 30        — negative counts back from the end
xs[1:3]     # [20, 30]  — a slice; stop is excluded
len(xs)     # 3
20 in xs    # True
```

If you ask for a position that doesn't exist, `xs[5]`, Python raises an error and stops. Slices, as before, never do.

**The membership check has a hidden cost, and this is the practitioner's detail.** When you write `20 in xs`, Python has no clever way to answer — it walks the list from the start, comparing each item, until it finds a match or runs out. On a list of a hundred, that's invisible. But put that check *inside* a loop over another ten thousand items and you've just asked Python to do a hundred million comparisons. Programs that mysteriously take minutes instead of milliseconds are very often this exact shape. Section 5 shows you the fix.

---

## 3. Changing a list

Lists are **mutable**, which is the word from unit 01 meaning "can be altered in place." Here's how.

```python
xs.append(40)          # add one item to the end
xs.extend([50, 60])    # add each item from another collection
xs.insert(0, 5)        # put something at a position, shifting the rest along
xs.remove(20)          # delete the first item equal to 20
last = xs.pop()        # remove the last item AND hand it back to you
first = xs.pop(0)      # same, but by position
```

`append` and `extend` look interchangeable and aren't, and getting them the wrong way round is a classic. `append` adds **one** thing. If that thing happens to be a list, you now have a list nested inside your list. `extend` unpacks the collection you give it and adds each item separately.

```python
xs = [1, 2]
xs.append([3, 4])      # [1, 2, [3, 4]]   — one new item, which is a list
xs = [1, 2]
xs.extend([3, 4])      # [1, 2, 3, 4]     — two new items
```

The nasty part is that the mistake doesn't fail where you made it. It fails later, when something tries to do arithmetic on `[3, 4]` and gets a confusing error a hundred lines away from the cause.

**The methods that return nothing.** This is worth its own moment, because it produces a specific, common, baffling bug.

```python
xs.sort()          # sorts the list itself, and returns None
xs.reverse()       # reverses the list itself, and returns None
```

Versus these, which leave the original alone and hand you a new one:

```python
ys = sorted(xs)              # xs is untouched
ys = list(reversed(xs))
```

So if you write `xs = xs.sort()`, here's what happens: the list gets sorted correctly, `.sort()` returns `None` because it has nothing to give you, and then you assign that `None` to `xs`, destroying your list. A few lines later something says `'NoneType' object is not iterable` and you have no idea why.

There is a rule underneath this that holds across the whole language, and knowing it means you never have to memorize the individual cases: **a method that changes something in place returns `None`; a built-in function that takes a collection returns a new one.** `.sort()` versus `sorted()`. `.reverse()` versus `reversed()`. Once you see the pattern, the behaviour stops being arbitrary.

---

## 4. Two list traps worth meeting before they happen

**Repeating a list.** You can build a list of a fixed size quickly:

```python
[0] * 3      # [0, 0, 0]
```

That's fine for numbers. It is a trap for anything mutable:

```python
rows = [[]] * 3
rows[0].append("x")
print(rows)          # [['x'], ['x'], ['x']]
```

You wanted three empty lists. You got **one** empty list with three references pointing at it — which is unit 01's "names, not boxes" showing up in a new outfit. Appending through one reference appends through all of them, because there's only one list there. Build it properly instead: `[[] for _ in range(3)]` creates three genuinely separate lists. (That's a comprehension, and unit 07 explains the syntax; for now just recognize the shape.)

**Copying.** Same idea, one level up:

```python
b = a              # NOT a copy. Two names, one list.
b = a.copy()       # a real copy of the outer list
b = a[:]           # identical to .copy()
```

But `a.copy()` is a **shallow** copy, meaning it makes a new outer list containing *the same inner objects*. That distinction is invisible until your list holds dictionaries — which, in this course, it always will. Copy a list of records, then edit `b[0]["name"]`, and `a[0]["name"]` changes too, because both lists are pointing at the identical dictionary.

If you genuinely need everything duplicated all the way down, that's `copy.deepcopy(a)`. But the cleaner discipline, and the one that dissolves this entire category of bug, is to stop mutating altogether: **build new data instead of editing old data.** Unit 07's comprehensions make that the path of least resistance, which is a large part of why Python code looks the way it does.

---

## 5. Aggregating a list

These are the built-in functions that take a whole list and give you one answer.

```python
sum(xs)          # add them up (numbers only)
min(xs)          # smallest
max(xs)          # largest
sorted(xs)       # a new list, in order
xs.count(10)     # how many times 10 appears
xs.index(20)     # the position of the first 20 (errors if there is none)
```

Two more that people underuse. `any()` is `True` if at least one item is truthy; `all()` is `True` only if every item is. Combined with the generator syntax you'll meet properly in unit 07, they turn a five-line loop-with-a-flag into one readable line:

```python
if any(r["status"] == "error" for r in rows):
    ...
if all(r.get("id") for r in rows):
    ...
```

Read those aloud — "if any row has status error" — and you can see why this is the idiom people reach for.

---

## 6. Tuples

**What it is.** A tuple is an ordered collection like a list, except **immutable** — once built, it cannot be changed. You write one with commas, and you should always add the parentheses even though they're often optional:

```python
point = (3, 4)
x, y = point           # pulling the two values back out
```

That second line is called **unpacking**, and it's one of the nicer things about Python. More on it in a moment.

One piece of syntax that catches everyone: a tuple with a single item needs a trailing comma, because the parentheses alone aren't what makes it a tuple — the comma is.

```python
one = (5,)          # a tuple containing 5
not_a_tuple = (5)   # just the number 5, in redundant brackets
```

**When to use which.** Reach for a tuple when the collection is a **fixed-size record whose positions each mean something specific** — `(year, month, day)`, `(latitude, longitude)`, `(name, count)`. Reach for a list when you have a **variable number of the same kind of thing**. That's the honest distinction, and it's about communicating intent to whoever reads the code next.

**But there are two reasons tuples matter beyond style**, and both are practical.

First, tuples are **hashable**, which is a word meaning "Python can compute a fixed fingerprint for this value, because it's guaranteed never to change." Only hashable things can be used as dictionary keys or set members (both of which are coming up). Lists can't be, because they could change underneath you and invalidate the fingerprint. Tuples can. Which means this works:

```python
counts[("US", 2024)] = 500
```

Counting by a **compound key** — sales per country per year, requests per endpoint per status — is an extremely common thing to need, and a tuple key is how you do it. Lists simply cannot.

Second, **returning several values from a function is just a tuple**:

```python
def min_max(xs):
    return min(xs), max(xs)

low, high = min_max([3, 1, 4])
```

There's no special "multiple return" feature in Python. The function builds a tuple and the caller unpacks it. That's it.

**Unpacking, since it comes up everywhere:**

```python
a, b = 1, 2
a, b = b, a                  # swap two values with no temporary variable
first, *rest = [1, 2, 3, 4]  # first = 1, rest = [2, 3, 4]
```

And it works in a loop header, which is where you'll use it most:

```python
for name, count in pairs:
    print(name, count)
```

The one thing that goes wrong: if the number of names doesn't match the number of values, Python raises `ValueError: too many values to unpack`. That happens in real life when an API changes the shape of what it returns, and the error message is at least honest about what happened.

---

## 7. Sets

**What it is.** A set is an unordered collection with **no duplicates**. You write it with curly braces:

```python
s = {1, 2, 3}
s = set([1, 1, 2, 2, 3])     # {1, 2, 3} — duplicates dropped automatically
```

One piece of syntax to memorize now: an empty set is `set()`, **not** `{}`. Empty curly braces mean an empty dictionary, which is unit 04's topic. Python had to pick one, and dictionaries won.

Members must be hashable, so a set can contain numbers, text, and tuples, but not lists or dictionaries.

**Why sets exist — and this is the part worth understanding rather than memorizing.** Two reasons, and both are about speed of thought as much as speed of execution.

The first is that membership testing is **instant**. Remember from section 2 that `x in some_list` walks the entire list. `x in some_set` doesn't walk anything — Python computes the fingerprint of `x` and looks directly at the one place it would have to be. It takes the same time whether the set holds ten items or ten million. If you're testing membership repeatedly, converting your list to a set first is often the entire performance fix.

The second is **set algebra**, which lets you express questions about overlap in one line:

```python
a = {1, 2, 3}
b = {2, 3, 4}

a | b     # {1, 2, 3, 4}   union — everything in either
a & b     # {2, 3}         intersection — only things in both
a - b     # {1}            difference — in a, not in b
a ^ b     # {1, 4}         in one or the other, but not both
```

Here's why that's genuinely useful rather than academic. Suppose you've pulled records from two different sources and you want to reconcile them:

```python
ids_a = {r["id"] for r in source_a}
ids_b = {r["id"] for r in source_b}

only_in_a = ids_a - ids_b
in_both   = ids_a & ids_b
```

Four lines, and you've answered "what do we have that they don't, and where do we agree." Written as nested loops that's eight lines, slower by orders of magnitude, and considerably harder to read aloud. This is the kind of thing that reads as fluency in an interview — not because it's clever, but because it's obviously the right tool.

**The two costs, which you must know about.**

Sets have **no order**. When you loop over one, the items come out in whatever order Python's internal storage happens to produce, and you must never rely on it. If you need predictable output, wrap it: `sorted(my_set)`.

And deduplicating **destroys information**. `set(names)` tells you which names appeared but not how many times each did. When the count is what you actually wanted, the tool is `collections.Counter`, which arrives in unit 16.

**The pattern worth memorizing.** These two costs collide in one common task — removing duplicates while keeping the original order — and the standard solution uses a set and a list together:

```python
seen = set()
out = []
for x in xs:
    if x not in seen:
        seen.add(x)
        out.append(x)
```

The set does the fast "have I seen this" checking; the list preserves the order. It comes up constantly, and it's better than `list(set(xs))` precisely because it doesn't shrug about the ordering.

---

## 8. Which one do I use?

| What you need | Reach for |
|---|---|
| Records in order, that will grow | `list` |
| A fixed-shape record, or a dictionary key | `tuple` |
| Membership tests, deduplication, overlap questions | `set` |
| Looking something up by name or ID | `dict` (unit 04) |
| Counts per category | `Counter` (unit 16) |

And the performance summary in one sentence: checking membership in a list scans it item by item, while checking membership in a set or a dictionary is instant regardless of size. At ten thousand items inside a loop, that's the difference between a program that finishes and one you kill.

---

## 9. What I have deliberately left out

The task needs some of these, and the rest are worth twenty seconds each. Find them in the interactive prompt.

- `enumerate()` — how to get the position *and* the item while looping.
- `zip()` — walking two lists side by side, and what it does when they're different lengths.
- `list.sort(key=...)` — unit 07 covers this properly, but look at it now.
- `set.update()` versus `set.add()`.
- `frozenset` — an immutable set, and why that's ever useful (hint: see "hashable" in section 6).

---

## 10. Check yourself

1. After `xs = [1,2]; ys = xs; ys.append(3)`, what is `xs`, and why?
2. What's the difference between `xs.append([1,2])` and `xs.extend([1,2])`?
3. Why does `xs = xs.sort()` destroy your list?
4. How do you create an empty set, and why isn't it `{}`?
5. Given two lists of IDs, how do you find the ones present in the first but not the second?
6. Why is `if x in big_list` inside a loop a performance problem?

*(Answers: 1. `[1, 2, 3]` — `ys = xs` created a second name for one list, not a copy. 2. append adds one item that happens to be a list; extend adds each item separately. 3. `.sort()` sorts in place and returns `None`, so the assignment overwrites your list with `None`. 4. `set()`; `{}` is an empty dictionary. 5. `set(a) - set(b)`. 6. list membership scans every item, so a loop over m items checking against a list of n does n×m comparisons.)*

---

*Carry three things forward. A list is your default container and it's what a JSON array becomes, so almost every response you handle starts life as one. Lists are mutable and assignment doesn't copy — which is unit 01's "names point at objects" appearing again, and it will appear a third time in unit 04 when you copy records. And sets exist to make two specific questions cheap: "have I seen this before" and "what overlaps between these two groups." Unit 04 introduces the last container, the dictionary, and that's the one that actually matches the shape of an API record.*

*Now open [`task.py`](task.py).*
