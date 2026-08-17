# 14 — Navigating Messy, Unfamiliar JSON

*About twenty-five minutes to read, thirty-five for the task, and it is worth every one of them. This is one of the two or three highest-value units in the course, so I want to say why before you start rather than after. Unit 12 taught you how to fetch a URL and get a response back. This lesson is about the four minutes immediately after that — the part where you are staring at a wall of unfamiliar JSON and somebody is watching you. Nothing here is assumed beyond unit 04, and where this builds on unit 04 I'll say so explicitly.*

---

## 1. The reason this unit matters more than it looks like it should

Here is the situation you are training for. An interviewer says: "here's an endpoint, have a look and tell me something interesting." They do not hand you documentation. They do not tell you what the fields mean. They hand you a URL, and the clock starts.

The failure mode is not that you can't write Python. The failure mode is that you spend eleven minutes scrolling through printed JSON, guessing at key names, and hitting the same error three times, and by the time you have found the data the conversation has moved on. The person who does well is not smarter — they have a *procedure*. They do the same six things in the same order every single time, and four minutes later they are talking about the data rather than about the shape of it.

This lesson is that procedure, written down.

Unit 04 taught you what nested data *is* — dictionaries inside dictionaries, lists of records, `.get()`, `or {}`. That was the vocabulary. This unit is the method for meeting a structure you have never seen and finding your way around it fast. Same material, completely different skill. Knowing what a dictionary is doesn't help if you don't know which of the eleven top-level keys holds the actual data.

And the destination never changes. Whatever arrives, you are trying to reach a **list of flat dictionaries** — the shape unit 04 ended on, the shape where every item is one row and every key is one column. `Counter`, `sorted`, `csv.DictWriter`, and pandas all accept that shape and nothing else. Getting there is the whole job; everything after it is easy.

Two words before we start, because I'll use them constantly.

A **record** is one item of data — one country, one search result, one user. In Python it's a dictionary. In SQL terms it's a row.

An **envelope** is packaging: an outer structure that wraps the records without being records itself. If a service replies with `{"hits": [...], "page": 0, "nbPages": 64}`, the outer dictionary is the envelope, the list under `"hits"` is the cargo, and `page` and `nbPages` are the shipping label. Almost every mistake beginners make in this unit is confusing the envelope for the cargo.

---

## 2. Step one: what shape is the top level?

Before anything else, ask Python what it just handed you. Two lines, always the same two lines:

```python
data = r.json()
print(type(data))
```

This is not a formality. `type()` from unit 01 is doing real work here, because the answer decides everything you do next. There are five shapes you will meet in practice, and each one has a recognition test and a follow-up move. The mental model to hold: **you have been handed a parcel, and your first job is to work out how many layers of packaging are between you and the contents.**

### Shape A — a plain list of records

```python
[{"id": 1, ...}, {"id": 2, ...}]
```

**How you recognise it.** `type(data)` says `list`, and `data[0]` is a dictionary that looks like actual data rather than a summary.

**What you do next.** Nothing, essentially. You are already at the target shape. Check how many you have and look at one of them:

```python
print(len(data))
print(json.dumps(data[0], indent=2)[:1500])
```

`json.dumps(obj, indent=2)` turns an object back into readable, indented JSON text — it's the single best way to actually *look* at a structure. The slice on the end is not fussiness; some records are two thousand lines long and dumping the whole thing scrolls everything useful off your screen.

### Shape B — a dict envelope

```python
{"hits": [...], "nbHits": 3200, "page": 0, "nbPages": 64}
```

**How you recognise it.** `type(data)` says `dict`, and when you print its keys, most of the values are small scalars and exactly one is a big list.

```python
print(list(data.keys()))
```

**What you do next.** Two jobs, and people usually only do the first. Job one is finding which key holds the real records, which is section 3 and is more interesting than it sounds. Job two is *reading the other keys*, because they are almost always pagination metadata and they are telling you something important: `nbPages: 64` means what you are holding is one sixty-fourth of the answer. If the question is "which of these is the most popular," an answer computed from page one of sixty-four is wrong. That's unit 15's problem, but noticing it is this unit's job.

### Shape C — a single entity

```python
{"login": "torvalds", "public_repos": 8, ...}
```

**How you recognise it.** `type(data)` says `dict`, but none of the values is a list of records. The keys are attributes of one thing, not sections of a document.

**What you do next.** Accept that you have one record and think about how you'd get many. Usually that means a second endpoint that lists IDs, then one request per ID in a loop — which immediately raises rate limits (unit 15) and doing them concurrently (unit 22). Say that out loud when it happens; recognising that "I need 200 of these" is a different problem from "I need one of these" is worth more than solving it quickly.

### Shape D — an array envelope

```python
[{"page": 1, "pages": 6, "total": 295}, [{...}, {...}, ...]]
```

**How you recognise it.** `type(data)` says `list`, but `len(data)` is 2, and the two elements are wildly different from each other — a small dictionary and then a big list.

This one deserves your attention because **nobody would ever guess it.** The World Bank's API genuinely replies like this: a two-element array where element 0 is the metadata and element 1 is the 295 actual countries. There is no documentation moment where you'd derive that; you find it only by looking. You will work against exactly this response in the task.

**What you do next.** Take element 1 — but not by hardcoding `data[1]`, for reasons in the next section.

### Shape E — parallel arrays

```python
{"time": ["2024-01-01", "2024-01-02"], "temperature": [4.1, 5.8]}
```

**How you recognise it.** `type(data)` says `dict`, and several values are lists of the *same length* containing plain scalars rather than dictionaries.

Open-Meteo replies like this, and it is the one shape that is genuinely not records at all. There is no dictionary anywhere that represents one day. What ties the data together is *position*: index `i` of every array belongs to the same moment. To get to the target shape you have to build the records yourself, zipping the arrays together into one dictionary per index.

There is a sixth shape you'll occasionally meet — a dictionary keyed by ID, `{"1": {...}, "2": {...}}`, where the keys are identifiers and the values are the records. Frankfurter's exchange-rate history does this with dates as keys. It's easy once you spot it: the records are `data.values()`, and if you need the key as a field, put it back in as you go.

---

## 3. Step two: finding the data key without guessing its name

This is the section that makes the whole toolkit work, so I want to be direct about why.

The beginner instinct with an envelope is to look at it, see `"hits"`, and write `data["hits"]`. That works — on that one endpoint, that one time. Change the API and it breaks, because the convention is not a convention at all. Different services call the same thing `data`, `results`, `items`, `records`, `hits`, `rows`, `content`, `entries`, `docs`, `payload`, or the plural of whatever resource you asked for. There is no standard. Memorising the list is not a strategy.

The strategy is to stop looking at the *name* and start looking at the *shape*:

> **The data is the value that is a non-empty list of dictionaries.**

That is the rule, and it's almost embarrassingly effective. Metadata is scalars — numbers, strings, booleans. Records are dictionaries. So sweep the values, keep the ones that are lists whose first element is a dictionary, and you have found your data on an API you have never seen, without knowing a single thing about it in advance.

**The practitioner's detail: prefer the longest.** Sometimes more than one value passes the test. Search APIs often return a `facets` or `aggregations` list alongside the results — a genuine list of small dictionaries that is not what you want. Break the tie by taking the longest list. The payload is essentially always bigger than any metadata list travelling with it, and "essentially always" is good enough for a four-minute exploration.

**The subtle part, which the task makes you handle.** Remember the World Bank shape, `[{...}, [...]]`. Look at what it satisfies. It *is* a list. Its first element *is* a dictionary. So a naive "is this already a list of records?" check says yes, and hands you back a two-item list — the envelope itself — instead of the 295 countries. It also contains an inner list of dictionaries, which is the answer you actually want.

Both descriptions are true of the same object, so the order in which you test them decides which answer you get. You have to look *inside* a list for a nested list of records **before** you accept the list itself. Get that order backwards and everything downstream is quietly, confusingly wrong: your record count is 2, your field profile is nonsense, and nothing raises an error to tell you. This is the single fiddliest thing in the unit, and it's the first function in the task.

---

## 4. Step three: taking inventory of one record

You have found the records. Now look at exactly one of them — not all of them, one — and find out what a record is made of.

The dump-and-scroll approach (`json.dumps(record, indent=2)`) works but is bad on a wide record, because a repository with eighty fields becomes three screens of text and you lose the forest. This loop is better, and it is worth memorising as a unit:

```python
record = records[0]
for key, value in record.items():
    print(f"{key:>24}  {type(value).__name__:10} {str(value)[:50]}")
```

It prints, for every field, its name, its type, and the first fifty characters of its value, one line each. Three columns, aligned, one screen. The `:>24` and `:10` are the f-string alignment codes from unit 02, and `type(value).__name__` gives you the type's name as plain text — `"int"`, `"str"`, `"dict"` — rather than the noisier `<class 'int'>`.

The reason types earn a whole column is that **the type of a field is what determines what you can do with it.** Which brings us to the part that is actually about analysis rather than about Python.

Once you can see the fields, sort every one of them into a bucket. Out loud, if there's an interviewer in the room. The buckets:

| Bucket | How you spot it | What it lets you do |
|--------|-----------------|---------------------|
| **Identifier** | unique-ish; named `id`, `key`, `slug`, or a URL | joining to other data, deduplicating |
| **Numeric** | `int` or `float` | sum, mean, min, max, distributions, "top ten" |
| **Categorical** | short strings that repeat, or booleans | grouping, counting, "how many per X" |
| **Temporal** | ISO date strings, or big integers that are epoch seconds | trends over time, bucketing by month |
| **Nested** | the value is a `dict` or a `list` | nothing yet — this has to be flattened first |

Those names are worth having. An **identifier field** names one thing uniquely. A **numeric field** holds a quantity you can do arithmetic on. A **categorical field** holds one of a smallish set of labels. A **temporal field** holds a point in time. And a **nested field** holds more structure inside it.

Here's why this is worth thirty seconds. When the interviewer follows up with "so what could you tell me from this?", the answer falls straight out of the classification: one categorical field plus one numeric field is a group-by. One temporal plus one numeric is a trend. Two identifiers pointing at different resources is a join. **You are not analysing the data yet — you are reading the menu of analyses the data makes possible**, and doing it in a structured way in front of somebody is a large part of what they are actually assessing.

One extra thing to check on a categorical field: its **cardinality**, which is just the number of distinct values it takes. `len(set(r.get("region") for r in records))` tells you in one line. It matters because it decides whether grouping by that field is useful. Cardinality of 7 gives you a nice summary table. Cardinality of 295 on 295 records means the field is really an identifier wearing a category's clothes, and grouping by it tells you nothing. Same instinct as choosing what to `GROUP BY` in SQL.

---

## 5. Step four: check that the fields are actually consistent

This is the step people skip, and it is the one that saves you from the worst failure mode in the unit. So it gets emphasis: **real responses lie about their schema.**

The lie is this. You look at record zero. It has fourteen fields. You reasonably conclude that the response has fourteen columns, you write code that reads all fourteen with square brackets, you set it running over a thousand records — and record 700 turns out not to have a `url` at all, and `KeyError` kills the job, and the 699 records you had already processed go in the bin. Unit 04 told you `.get()` exists for this reason. This section is how you find out *which* fields need it, before you write a single line that touches them.

The tool is `Counter` from the `collections` module — a dictionary specialised for counting. You feed it things and it keeps a tally:

```python
from collections import Counter

key_counts = Counter()
for record in records:
    key_counts.update(record.keys())
```

`.update()` on a `Counter` takes any collection and adds one to the tally for each item in it. So after that loop, `key_counts["url"]` is the number of records that had a `url` key at all. Compare each tally against the total number of records, and every field that falls short is a field you cannot trust:

```python
n = len(records)
for key, count in key_counts.most_common():
    if count < n:
        print(f"{key}: present in only {count}/{n}")
```

That is ten seconds of work and it converts an unknown risk into a written list. Anything it prints must be read with `.get()`. Anything it doesn't print is safe with square brackets. Think of it as **taking the register**: you call every field's name and see how many records answer.

**The practitioner's detail, and it's a real one.** Presence is not the same question as emptiness, and checking only presence will still let you down. A field can be in every single record and hold `null` in most of them — the key is there, so `"url" in record` says `True` and `Counter` counts it as present, and you still get `None` when you read it. So count nulls separately:

```python
nulls = {k: sum(1 for r in records if r.get(k) is None) for k in key_counts}
```

(The `sum(1 for ...)` shape is unit 07's; read it for now as "count the records where this is true.")

Present-but-null is exactly the case unit 04 warned you about when it explained why `or {}` beats a `.get()` default, and it's why this function counts `present` and `null` as two separate numbers rather than one. They answer different questions: *can I use square brackets on this?* and *is there actually any data in here?*

The null rate is also a genuinely good thing to say out loud. "`location` is null for sixty percent of these records, so I'm not going to group by it — the answer would mostly be a bucket called None" is the kind of remark that marks you as someone who has handled real data rather than examples.

One more thing worth profiling while you're here: the set of *types* each field takes across all the records. If a field reports one type, fine. If it reports two, something is wrong, and it's usually one of two things — a numeric field that arrives as a string in some records and a number in others, or a field that is a dictionary when populated and `null` when not. Either way a mixed-type field is a warning sign rather than a curiosity, because it means any arithmetic or sorting you do on it will behave differently depending on the record.

---

## 6. Step five: getting down into the nesting

Unit 04 covered the mechanics here, so this is a refresher plus the parts that only bite on real data. Reading nested data is just repeated indexing, each step handing you another object to index:

```python
repo["owner"]["login"]
pokemon["types"][0]["type"]["name"]
```

The mental model, and it is the one that keeps you out of trouble: **every square bracket is a step, and any step can be a hole in the floor.** `repo["license"]["name"]` looks like one operation but is two, and the first one can perfectly legitimately return `None`, at which point the second one raises `TypeError: 'NoneType' object is not subscriptable`. Unit 04 called this the most common runtime error in API work and I stand by it.

Your defences, in escalating order of depth:

```python
(repo.get("license") or {}).get("name")           # one or two levels
deep_get(repo, "stats", "watchers", "total")      # three or more
```

`or {}` says "give me the licence, or an empty dictionary if that came back falsy" — and an empty dictionary answers `None` to any key, so the chain ends safely rather than exploding. It beats `repo.get("license", {})` because a default only fires when the key is *absent*, while `or {}` also catches the key being present and holding `null`, which is the more common shape in real JSON. `deep_get` is the helper you wrote in unit 04; past two levels, chained `or {}` becomes unreadable and the helper is the right answer.

Lists inside records need the same care, and get it less often:

```python
topics = repo.get("topics") or []          # never None
first = topics[0] if topics else None      # never IndexError
```

`data["results"][0]` is a landmine. It works for as long as every search you try happens to match something, and goes off the first time one doesn't.

---

## 7. Walking an unknown structure to discover where things live

Sometimes the structure is deep enough that eyeballing it doesn't work. PokéAPI's response for a single Pokémon is roughly eight hundred lines of JSON, and the question "where in here is the type name?" is not answerable by scrolling.

So instead of reading it, index it. The idea is to visit every value in the whole structure and print the *path* you took to reach it — `types[0].type.name` — so that eight hundred lines of nesting becomes a flat, searchable list of addresses. Think of it as **generating a postal address for every value in the response.** Once you have that list, "where's the name?" is a substring search, and it takes one second instead of five minutes.

```python
def walk(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from walk(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from walk(value, f"{path}[{i}]")
    else:
        yield path, obj

for path, value in walk(pokemon):
    if "name" in path:
        print(path, value)
```

There are two ideas in those twelve lines that are worth naming properly.

The first is **recursion** — a function that calls itself. You met it once, in unit 04's `flatten_dict`, and once is not enough for it to feel natural, so here it is again in the way that makes it click. The function's job is "describe everything inside `obj`, given that you got here by the path `path`." If `obj` is a dictionary, it can't answer directly, but it *can* say: for each key, the thing inside it needs describing too, and the path to get there is my path plus that key. So it hands the smaller problem to itself with a longer path. The `path` parameter is the whole trick — it is the trail of breadcrumbs, carrying where-you-have-been-so-far down into each nested call. Every call goes one level deeper and one segment longer, until it reaches something that isn't a container and there's nothing left to descend into. That's the base case, and every recursive function needs one or it never stops.

The second is a **generator**. `yield` is like `return` except the function doesn't finish — it hands one value back to whoever is looping over it and then picks up where it left off on the next go round. `yield from` means "yield everything that this other generator yields," which is how the results from a nested call flow back up to the top. Generators produce values lazily, one at a time, instead of building the whole list in memory. It's genuinely useful on big responses. It is also entirely optional here: you can write the same function returning a plain list, accumulating with `out.extend(...)` instead of `yield from`, and that's the version the task asks for precisely because recursion is quite enough new machinery for one function.

**The practitioner's detail here is a small design decision with a good reason.** An empty dictionary or an empty list counts as a **leaf** — a stopping point, reported with its own path — rather than as a container to descend into. That looks like a special case and isn't. Descending into an empty container produces nothing at all, so the path to it would silently vanish from your index, and the fact that `adminregion` is present-but-empty is exactly the kind of thing you wanted the index to tell you. There is nothing inside to describe, so you describe the container itself.

And here's the payoff, which the task's test actually checks. Search PokéAPI's response for paths containing `stat.name` and you get seven hits, not the six you'd expect from the six visible stats. The seventh lives under `past_stats`, a field you would never have known was in there. That is the entire argument for searching rather than guessing.

---

## 8. Step six: flatten to records

**Flattening** means taking a nested structure and producing a flat one — pulling values up out of their nesting and giving each a single top-level key, so that what was `record["license"]["name"]` becomes `row["license"]`. It's the last step of the procedure and the one that makes everything afterwards easy.

The shape you are flattening *to* never changes: a list of flat dictionaries, one per record, no nesting left anywhere. Every tool downstream — `Counter`, `sorted`, `csv.DictWriter`, `pd.DataFrame` — takes that and nothing else.

```python
rows = [
    {
        "name": r["name"],
        "owner": (r.get("owner") or {}).get("login"),
        "stars": r.get("stargazers_count") or 0,
        "license": (r.get("license") or {}).get("name"),
    }
    for r in raw
]
```

Notice three things about that. Every optional field is read defensively. Every nested value is pulled up to the top level with a plain name. And crucially, **the field names are yours now** — `stars` rather than `stargazers_count`, `license` rather than a two-level path. Once the data is in your shape, the API's naming choices stop being your problem.

**The practitioner's detail: pick five to ten fields, not eighty.** The instinct when flattening is to keep everything, on the grounds that you might need it. Resist it. A narrow record prints on one line, is readable when you dump it, and makes the eventual bug obvious. A record with eighty columns is the same wall of JSON you started with, only now it's your fault. You can always go back for another field; you cannot easily un-drown.

---

## 9. Two traps that are real, not hypothetical

Both of these are in the World Bank data you'll work against in the task, which is why I'm flagging them rather than leaving them for you to discover at a bad moment.

**Numbers arriving as strings.**

```python
{"population": "1400000", "latitude": "12.5167"}
```

APIs do this constantly, often because whatever produced the JSON was serialising from a database that stored everything as text. The reason it's dangerous rather than annoying is that nothing raises. Sorting works. Comparing works. They just give you the wrong answer, because comparing strings is **lexicographic** — character by character, like a dictionary — so `"9"` sorts above `"1400000"` for the same reason "z" comes after "apple". You get a plausible-looking ranking that happens to be nonsense, and nothing in the output says so.

So convert explicitly, and tolerate failure while you do it, because some of the values will be empty:

```python
def as_number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
```

That's unit 08's `try`/`except` doing exactly what it's for: `float("")` and `float(None)` both raise, and this hands back `None` instead of stopping your program.

**Empty string used instead of null.** The World Bank returns `{"id": "", "iso2code": "", "value": ""}` for a nested reference that simply doesn't apply — an aggregate row like "World" has no administrative region, so rather than sending `null` it sends blanks. This is worse than `null` because `""` is a string, so a type check says "string, fine" and it sails through into your output as an empty column. Normalise it as it arrives: `value.strip() or None` both trims the whitespace and turns anything blank into `None`, using unit 01's truthiness rules to do it in one expression.

While you're stripping — trailing spaces on values are real too. The World Bank's region values arrive as `"Latin America & Caribbean "`, with a space on the end. Group by that without stripping and you can end up with two buckets that look identical on screen and are not equal to Python.

---

## 10. Look this up yourself

Reading documentation under time pressure is the most transferable skill in this course, so as usual a few things are deliberately left for you:

- `collections.Counter` — particularly `.update()` with an iterable of keys, and `.most_common()`.
- `json.dumps(obj, indent=2)[:2000]` — try it without the slice on the PokéAPI fixture once, to see why the slice is there.
- `isinstance(x, (list, tuple))` — passing a tuple of types to check against several at once.
- `urllib.parse.urlparse` — specifically what `.netloc` gives you, since you need the host out of a URL in the task.
- `pprint.pprint` — an alternative way of looking at a structure; decide which you prefer.
- `zip()` — the tool you'd reach for to turn Open-Meteo's parallel arrays into records.

---

## 11. Check yourself

1. What are the five top-level shapes a response can arrive in, and how do you tell an array envelope from a plain list of records?
2. How do you find the data key in an envelope without knowing its name?
3. Why does the World Bank's `[metadata, records]` shape make the order of your checks matter?
4. Why is `(r.get("license") or {}).get("name")` better than `r.get("license", {}).get("name")`?
5. How do you detect that some records are missing a field — and why isn't that enough on its own?
6. What goes wrong, and what doesn't go wrong, when you sort numbers that arrived as strings?
7. What shape are you always trying to reach before you analyse anything?

*(Answers: 1. a list of records; a dict envelope; a single entity; an array envelope; parallel arrays. An array envelope is a list of length two whose elements are of different kinds — a small metadata dict and a big list. 2. look for the value that is a non-empty list of dictionaries, and take the longest if several qualify. 3. because it satisfies both "is itself a list of records" and "contains a list of records", so whichever you test first is the answer you get, and only one of them is right. 4. a default only applies when the key is absent, while `or {}` also handles the key being present and holding null. 5. a `Counter` over every record's keys, compared against the record count — and it isn't enough because a key can be present in every record and hold `null` in most of them, so you count nulls separately. 6. the sort silently succeeds and gives the wrong order, because string comparison is lexicographic — `"9"` above `"1400000"` — and nothing raises. 7. a list of flat dictionaries.)*

---

*Three things to carry out of this unit. First, the procedure itself: check the top-level type, find the records by shape rather than by name, inventory one record and classify its fields, take the register of which fields are actually present and filled in, then flatten to a list of flat dictionaries. Doing those in that order is the difference between four minutes and fifteen. Second, look for shapes, not names — the reason the toolkit works on an API you have never seen is that it never assumes anybody called anything anything in particular. Third, real data is inconsistent by default: fields go missing, nulls arrive as empty strings, numbers arrive as text, and none of it raises an error to warn you. Assume it, check for it, and say what you found out loud.*

*The task builds this as an actual toolkit — five general functions you should genuinely keep and point at any endpoint, then four that apply them to three real, awkward responses. Unit 15 is the other half of the same story: what you do once you realise `nbPages` was 64.*

*Now open [`task.py`](task.py).*
