# 04 — Dictionaries and Nested Data

*This is the most important lesson in Part 1, and it's the longest — about twenty minutes. If you only get one unit properly solid before your interview, make it this one. Everything in Part 2, where you actually call live APIs, assumes you are fluent here. Read straight through; nothing is assumed beyond units 01 to 03.*

---

## 1. Why this unit is the one that matters

A JSON response is made of exactly two kinds of grouping. Unit 03 covered the first — arrays, which become Python lists. This unit covers the second, and it's the one that carries all the actual information.

```
{"login": "torvalds", "id": 1024025, "followers": 200000}
```

Curly braces, with labels attached to values. In JSON that's an **object**. In Python it becomes a **dictionary**, usually written `dict`.

Here's the thing to internalise: *a JSON object is not merely similar to a Python dictionary — after parsing, it literally is one.* When you fetch a URL and call `.json()`, what you get back is a dictionary, or a list of dictionaries, and nothing else. So being fluent with dictionaries is not preparation for handling API data. It **is** handling API data.

If SQL is your background, the mapping is clean: one dictionary is one row, the keys are the column names, and a list of dictionaries is your result set. The differences are that every row can carry a different set of columns — a problem you will spend real time on — and that a value can itself contain more rows nested inside it, which is the other problem.

---

## 2. What a dictionary is

**What it is.** A dictionary maps **keys** to **values**. You write it with curly braces and colons:

```python
user = {"login": "torvalds", "id": 1024025, "followers": 200000}
```

You get a value out by putting its key in square brackets:

```python
user["login"]        # "torvalds"
len(user)            # 3
"login" in user      # True
```

Watch that last line carefully: `in` on a dictionary checks the **keys**, not the values. `"torvalds" in user` is `False`, because that's a value. It trips people up once.

Keys must be hashable — that word from unit 03 meaning "guaranteed not to change, so Python can fingerprint it." In practice keys are text almost always, sometimes numbers, occasionally tuples when you need a compound key. Values can be absolutely anything, including other dictionaries and lists, which is where section 6 goes.

**Why dictionaries are everywhere.** Two properties. First, looking something up is **instant and stays instant** — a dictionary with a million keys answers as fast as one with three, because Python computes the key's fingerprint and jumps straight to the right place rather than searching. Second, since Python 3.7 dictionaries **remember the order you inserted things in**, so when you build a record and then print it or write it to a CSV, the columns come out in the order you wrote them rather than scrambled. You'll rely on both of those without ever thinking about them.

---

## 3. `.get()` — the single most important method in this course

I'm giving this its own section because it genuinely deserves one.

**What it is.** Square brackets are one way to read a key. `.get()` is the other:

```python
user["login"]               # "torvalds"
user["company"]             # ERROR — that key doesn't exist, program stops
user.get("company")         # None — no error
user.get("company", "n/a")  # "n/a" — you choose what to get instead
```

The difference is entirely in what happens when the key isn't there. Square brackets raise a `KeyError` and halt everything. `.get()` quietly hands you `None`, or a default you specify.

**Why this matters far more than it looks like it should.** Because *real API responses do not have consistent fields.* This isn't an edge case, it's the normal state of affairs. On GitHub, a few users have a `company` set and most don't. Plenty of repositories have `null` where a licence would be. The World Bank sends an empty string for missing values. TVmaze returns records where `network` is filled in and records where it's `null` because the show was web-only.

So picture yourself looping over five hundred users, pulling out their company:

```python
names = [u["company"] for u in users]      # fragile
```

That runs beautifully for thirty-six records and then dies on the thirty-seventh, throwing away everything it had already done. Written the other way, every record survives and `None` marks the ones that had nothing:

```python
names = [u.get("company") for u in users]  # robust
```

**When to use which — a judgment call, not a rule.** Use square brackets when a missing key would be a genuine bug that you *want* to hear about loudly and immediately. Use `.get()` when absence is legitimate data. With external APIs, absence is nearly always legitimate.

Saying that reasoning out loud in an interview — *"I'm using `.get()` because this field is optional on their side, and I'd rather produce a null than crash on record seven hundred of a thousand"* — is exactly the kind of thing that separates someone who has handled real data from someone who has only handled examples.

**One subtlety, which the task turns into an exercise.** `.get()` returns `None` in two different situations: when the key is missing entirely, and when the key is present holding `null`. Usually you don't care, since both mean "no data here." When you *do* care, `"key" in d` distinguishes them, because that asks only whether the key exists.

---

## 4. Building and changing dictionaries

```python
d["new"] = 1                    # add a key, or overwrite an existing one
d.update({"a": 1, "b": 2})      # add or overwrite several at once
del d["a"]                      # remove a key (errors if it isn't there)
value = d.pop("a", None)        # remove it and hand it back, with a default
```

To combine two dictionaries into a new one:

```python
merged = {**d1, **d2}      # wherever they disagree, d2 wins
merged = d1 | d2           # identical, Python 3.9 and later
```

The `**` means "unpack this dictionary's contents into the one being built." You'll meet the same symbol in unit 06 doing the same job for function arguments.

**The grouping idiom, which you will use constantly.** You have a pile of records and you want them sorted into buckets by one of their fields — the equivalent of SQL's `GROUP BY`. The tool is `setdefault`:

```python
groups = {}
for record in records:
    groups.setdefault(record["type"], []).append(record)
```

`setdefault(key, default)` does two things at once: if the key exists it returns its current value; if it doesn't, it inserts your default and returns *that*. So the line reads as "get me the list for this type, creating an empty one if this is the first time I've seen it, and append to it."

Without it, `groups[key].append(...)` fails on the first record of every new group, because the key doesn't exist yet. Three lines, and you can group anything by anything. There's a slightly cleaner alternative called `collections.defaultdict` in unit 16 — know both, and reach for `setdefault` when you're typing fast, since it needs no import.

---

## 5. Looping over a dictionary

```python
for key in d:                    # gives you the keys
for value in d.values():         # gives you the values
for key, value in d.items():     # gives you both
```

The third form is the one you want almost always. `.items()` produces `(key, value)` pairs, which the loop header unpacks using unit 03's unpacking. If you catch yourself writing `for k in d:` and then `d[k]` on the very next line, that's `.items()` asking to be used.

One rule with teeth: **never add or remove keys while you're looping over a dictionary.** Python notices and raises `RuntimeError: dictionary changed size during iteration`. When you need to, loop over a snapshot instead — `for k in list(d.keys()):` builds a separate list of keys first, so modifying the dictionary afterwards is safe.

---

## 6. Nesting — the actual shape of real data

Everything so far has been flat. Real responses are not. Here's a trimmed but genuine GitHub repository record:

```python
repo = {
    "id": 1296269,
    "name": "Hello-World",
    "owner": {
        "login": "octocat",
        "type": "User",
    },
    "topics": ["demo", "example"],
    "license": None,
    "stats": {
        "forks": 1000,
        "watchers": {"total": 80, "unique": 60},
    },
}
```

Notice what's happening. The value under `"owner"` is another dictionary. The value under `"topics"` is a list. The value under `"stats"` is a dictionary containing yet another dictionary. And `"license"` is `None`, because this repository doesn't have one.

**Reading it is just repeated indexing.** Each step hands you another object, and you index *that*:

```python
repo["owner"]["login"]                 # "octocat"
repo["topics"][0]                      # "demo"
repo["stats"]["watchers"]["total"]     # 80
```

Read the last one left to right as a sentence: take the repo, get its stats, get the watchers out of that, get the total out of that. There is no special nesting syntax — it's the same square brackets you already know, used repeatedly.

The only thing you need to track is **what kind of thing you're holding at each step**, because dictionaries are indexed by key and lists by number. When you lose track — and on a deeply nested response you will — the fastest recovery is to stop guessing and look:

```python
print(type(repo["stats"]))     # is this a dict or a list?
```

Two minutes doing that in the interactive prompt beats twenty minutes of guessing, and doing it in front of an interviewer reads as normal professional behaviour rather than confusion.

---

## 7. Where nesting breaks, and the three ways to survive it

This section is the practical heart of the lesson. What follows is, without much competition, **the most common runtime error people hit when working with API data.**

```python
repo["license"]["name"]
# TypeError: 'NoneType' object is not subscriptable
```

Read that message carefully, because it's telling you exactly what happened. `repo["license"]` worked fine — it returned `None`, because that's genuinely what's stored there. Then you tried to look up `"name"` inside `None`, and `None` contains nothing. "Not subscriptable" is Python's way of saying "you can't put square brackets on this thing."

And here's the part that surprises people: **`.get()` does not save you.**

```python
repo.get("license").get("name")     # exactly the same error
```

Of course it doesn't. The first `.get()` succeeded and returned `None`. Then you called `.get()` on `None`, and `None` has no methods. `.get()` protects you from a *missing key*. It does nothing about a key that exists and holds nothing.

There are three ways out, and which you choose depends on how deep you're going.

**First: `or {}`, for one or two levels.**

```python
(repo.get("license") or {}).get("name")     # None, no crash
```

Read it as: "give me the licence, or an empty dictionary if that's falsy, then ask *that* for its name." An empty dictionary answers `None` to any key you ask it for, so the chain terminates safely instead of exploding.

You'll also see `repo.get("license", {})` written for the same purpose, and it is *almost* as good — but not quite, and the difference is the practitioner's detail worth carrying out of this lesson. **A default only applies when the key is absent.** If the key is present holding `null`, then `.get("license", {})` dutifully returns `None` and you crash anyway. `or {}` catches both cases, because `None` is falsy — which is unit 01's truthiness rules paying off. Since present-but-null is the more common shape in real JSON, `or {}` is the one to reach for. You'll use it in this task, and again in unit 09 against genuinely null licences in real GitHub data.

**Second: catching the error rather than preventing it.** That's `try`/`except`, and it's unit 08. It's often the cleanest answer, and you'll rewrite some of this lesson's work using it there.

**Third: a reusable helper, which is the right answer past two levels.** Chaining `or {}` three times is unreadable, so you write one small function once and keep it forever:

```python
deep_get(repo, "stats", "watchers", "total")     # 80
deep_get(repo, "license", "name")                # None, instead of an explosion
```

Writing `deep_get` is the first thing this unit's task asks of you, and I'd encourage you to genuinely keep it afterwards. Having it in your head during an interview is worth real minutes, because messy nesting isn't a possibility — it's a certainty.

**Lists inside records need the same care.** Never index a list from an API without checking there's something in it:

```python
topics = repo.get("topics") or []          # never None
first = topics[0] if topics else None      # never an IndexError
```

`data["results"][0]` is a landmine, and it goes off the first time a search returns nothing.

---

## 8. Turning a list of records into a lookup table

**What it is.** You have a list of records and you need to find one by its ID. The naive approach searches the list every time. The right approach builds a dictionary once:

```python
by_id = {u["id"]: u for u in users}
by_id[1024025]["login"]
```

That curly-brace-with-a-`for` is a **dictionary comprehension**; unit 07 explains the syntax properly. For now read it as "build a dictionary where each user's id points at that user."

**Why it's worth doing.** Searching a list is a scan — check every record until you find the match. Doing that once is fine. Doing it inside a loop over another list is unit 03's performance trap wearing a new hat: ten thousand lookups against a ten-thousand-record list is a hundred million comparisons. Building the dictionary costs one pass, and every lookup afterwards is instant.

**Where it shows up.** This *is* a join. When an interviewer asks you to combine two sources — posts with their authors, transactions with their customers — the shape of the answer is: index one side into a dictionary, then walk the other side once and look each match up. That's the same algorithm a database performs internally for a hash join, and doing it deliberately rather than with nested loops is both faster and considerably easier to explain out loud. You'll write exactly this in unit 16.

---

## 9. Rearranging dictionaries

Three patterns you'll want, written as comprehensions (unit 07 covers the syntax — recognize the shape for now):

```python
{v: k for k, v in d.items()}                   # swap keys and values
{k: v for k, v in d.items() if v is not None}  # drop the empty fields
{k.lower(): v for k, v in d.items()}           # normalize the key names
```

The first is lossy in a way worth noticing: if two keys share a value, inverting silently keeps only the last one. Fine for building a lookup table, wrong for almost anything else.

The third is more useful than it looks. Different APIs name the same concept differently — `userName`, `user_name`, `USER_NAME` — and normalizing keys as data arrives means everything downstream can stop caring. You built a version of this in unit 02's task, and you'll use it again in unit 18.

---

## 10. Records: the list-of-dictionaries shape

Put units 03 and 04 together and you get the shape this whole course is aimed at:

```python
users = [
    {"login": "a", "followers": 10},
    {"login": "b", "followers": 30},
]
```

A list of flat dictionaries. This is what pandas accepts, what the CSV writer accepts, what FastAPI serializes back to JSON without complaint. **Whatever mess arrives, your first transformation is to get to this shape** — and once you're there, the rest of the task is easy. That sentence is worth remembering, because it's the plan for the first five minutes of almost any data question you'll be asked.

Things you'll do to it constantly:

```python
total = sum(u["followers"] for u in users)
names = [u["login"] for u in users]
top   = max(users, key=lambda u: u["followers"])
```

That last line deserves a note, because the distinction catches people under pressure. `max(u["followers"] for u in users)` gives you `30` — the biggest number. `max(users, key=...)` gives you `{"login": "b", "followers": 30}` — the whole record. Usually you want the record, because "who has the most" is a more useful answer than "the most is 30." Unit 07 covers `key=` and `lambda` properly; for now just note that the two forms hand back different kinds of thing.

---

## 11. The JSON to Python translation table

This is the entire mapping, and it's worth actually memorizing:

| JSON                     | Python               |
| ------------------------ | -------------------- |
| object`{...}`          | `dict`             |
| array`[...]`           | `list`             |
| string                   | `str`              |
| number without a decimal | `int`              |
| number with a decimal    | `float`            |
| `true` / `false`     | `True` / `False` |
| `null`                 | `None`             |

There's one asymmetry that will eventually confuse you, so meet it now: **JSON object keys are always text.** If you have a dictionary keyed by integers, save it as JSON, and load it back, your keys return as strings — `1` becomes `"1"`. The IDs that used to match suddenly don't, and nothing warns you. When a lookup mysteriously stops working after a save-and-reload cycle, this is why.

---

## 12. What I have deliberately left out

- `dict.pop()` versus `del` — and when you'd want the removed value back.
- `dict.fromkeys()` — building a dictionary of defaults in one line.
- `collections.defaultdict` — skim it now; unit 16 uses it properly.
- What `d.keys() & other.keys()` does, and why a dictionary's keys support unit 03's set operations.
- Why `{"a": 1} == {"a": 1}` is `True` while `{"a": 1} is {"a": 1}` is `False`. (Unit 01, section 4, contains the answer.)
- `json.dumps(obj, indent=2)` — your best tool for actually *looking* at a nested structure. You'll use this constantly from unit 12 onward.

---

## 13. Check yourself

1. What's the difference between `d["x"]` and `d.get("x")` when `x` isn't there?
2. Why does `repo.get("license").get("name")` still crash when `license` is `null`?
3. How do you group a list of records by one of their fields, in three lines?
4. Does `max(users, key=lambda u: u["followers"])` return a number or a dictionary?
5. What happens to integer dictionary keys after a round trip through JSON?
6. How do you turn a list of records into something you can look up by ID?

*(Answers: 1. square brackets raise `KeyError` and stop the program; `.get()` returns `None`. 2. the first `.get()` succeeds and returns `None`, then you call `.get()` on `None`, which has no methods. 3. `groups.setdefault(record[key], []).append(record)` inside a loop. 4. the dictionary — the whole record. 5. they become strings. 6. `{r["id"]: r for r in records}`.)*

---

*This is the unit whose ideas you'll use every day of the rest of the course. Four things to carry forward: a parsed JSON response is literally dictionaries and lists, so there is no translation layer to learn beyond the table above; `.get()` and `or {}` exist because real records are missing fields, and you cannot let record 700 kill a job that has already processed 699; the target shape for everything is a list of flat dictionaries, and reaching it is the first move of any data task; and dictionary lookup is instant, which is why turning a list into a lookup table is what a join actually is underneath. Unit 05 is control flow — loops and conditions — which is what finally lets you do all of this to five hundred records instead of one.*

*Now open [`task.py`](task.py).*
