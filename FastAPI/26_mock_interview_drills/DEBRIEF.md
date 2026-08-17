# Drill Debriefs

**Read each section only after you have done that drill.** Reading ahead turns a drill into a tutorial and destroys the one thing it was for — the value is entirely in meeting the data cold, and you only get to do that once per endpoint.

*What follows is what is actually in each response, what you should have noticed, and what a strong answer looks like. It is not a solution file; there is no correct output to match. Read your drill's section, compare it against what you did, and be specific with yourself about which of the gaps was a knowledge gap and which was a habit. Almost all of them will be habits.*

---

## Drill 1 — Cold open

### What the data actually is

`https://api.openbrewerydb.org/v1/breweries` returns a **plain list of flat dicts** — shape A from unit 14, the friendliest one there is. No envelope wrapping the records, no metadata alongside them, no nesting inside them. `type(data)` says `list`, `data[0]` is a dictionary of scalars, and you are already at the target shape without doing anything.

Now classify the fields the way unit 14 taught, because the classification is what tells you which analyses are even possible.

The **identifiers** are `id`, a UUID string, and `name`, which is identifier-*ish* — near-unique in practice but not guaranteed and not something you'd join on.

The **categoricals** are where all the interesting analysis lives. `brewery_type` is the good one: a short repeating string taking values like `micro`, `brewpub`, and `large`, with low cardinality, which is exactly what makes it worth grouping by. Then there's a hierarchy of geographic categoricals — `city`, `state_province`, `state`, `postal_code`, and `country` — where each level is a coarser bucket than the one below it.

The **numerics** are `longitude` and `latitude`, and both come with a warning attached: they arrive as *strings*, and they are often null.

The **mostly-empty** fields are `address_1`, `address_2`, `address_3`, `phone`, and `website_url`. They are present as keys but null on most records, which as unit 14 §5 insisted is a different fact from being absent, and one you only find by counting nulls separately from counting keys.

And then the observation that matters most: **there is no temporal field at all.** Not one. Worth saying out loud in the room: *"there's no timestamp anywhere here, so no trend analysis is possible — this is purely categorical and geographic."* Noticing what you *can't* do with a dataset is as useful as noticing what you can, and it is the sort of remark that lands as data sense rather than as an excuse.

### What you should have caught

Three things, in rough order of how badly each one bites.

The first is that `latitude` and `longitude` are strings. This is unit 14 §9's trap arriving in the wild, and the reason it's dangerous rather than annoying is that nothing raises: `sorted(records, key=lambda r: r["latitude"])` runs perfectly happily and hands you a lexicographic ordering — character by character, like a dictionary — which is nonsense as geography and looks entirely plausible on screen.

The second is that `state` and `state_province` duplicate each other. Redundant fields are extremely common in real responses, usually the fossil of some earlier schema. Pick one, and say which and why.

The third is that roughly a third of the records have no coordinates at all. Any map, any distance calculation, any geographic clustering has to decide what to do about that up front rather than discovering it halfway through.

### Three analyses this supports

Breweries per state; brewery-type mix per state; and geographic clustering — with a large caveat attached about the missing coordinates. Note that all three fall straight out of the classification above: categorical alone gives you a count, categorical plus categorical gives you a mix, numeric pair gives you geography. You are reading the menu, not cooking yet.

### If you took longer than 15 minutes

You almost certainly spent the extra time reading raw JSON in the terminal, scrolling up and down looking for field names. That is the failure mode, and the fix is mechanical rather than clever — these two snippets, typed by reflex the moment the response lands:

```python
print(json.dumps(data[0], indent=2))
for key, value in data[0].items():
    print(f"{key:>18}  {type(value).__name__:8} {str(value)[:40]}")
```

The first shows you one record properly indented. The second gives you every field's name, type, and a sample of its value, three aligned columns on one screen. Together they take about ten seconds and they replace the five minutes of scrolling entirely.

---

## Drill 2 — Aggregate and rank

### The shape of a good answer

Counting per state is one line with `Counter`, and printing it as an aligned table is one more:

```python
from collections import Counter

per_state = Counter(r["state"] or "unknown" for r in records)
for state, count in per_state.most_common(10):
    print(f"{state:<22} {count:>5}")
```

Note the `or "unknown"` sitting inside the generator expression. That is the null-handling decision being made explicitly, in the place where the data enters your count, rather than being discovered later.

For the type mix you need to group first and then compute a share within each group. Grouping by hand with `setdefault` is perfectly good here — `setdefault(key, [])` hands you the list already stored under that key, or puts an empty one there and hands you that:

```python
by_state = {}
for r in records:
    by_state.setdefault(r["state"] or "unknown", []).append(r)

for state, rows in by_state.items():
    micro = sum(1 for row in rows if row["brewery_type"] == "micro")
    share = micro / len(rows) * 100 if rows else 0
```

The `if rows else 0` on the last line is unit 01's division guard. It cannot actually fire here, because a key only exists in `by_state` if something was appended to it — but writing it anyway is the habit, and the habit is what saves you on the day the grouping comes from somewhere less well-behaved.

### The data-quality sentence

Something along these lines: *"About a third of records have no coordinates, and `state` is null for all non-US breweries, so I'm bucketing those as 'unknown' rather than dropping them — dropping would understate the international count."*

That sentence is worth more than the entire table above it, and it is worth understanding why rather than just repeating it. It shows three separate things in one breath: that you looked at the data rather than assuming it, that you made a decision about the nulls rather than letting a default happen to you, and that you can justify the decision in terms of what it would do to the answer. Volunteering it unprompted is the whole move.

### Common mistakes

Reaching for pandas to handle 200 flat records is the most common one. It works, and it isn't wrong exactly, but for a couple of hundred rows it is slower to write and harder to talk through than `Counter`, and Playbook §9 lists it as an anti-pattern for exactly that reason.

Sorting with `sorted(..., reverse=True)` and forgetting the tie-break is the subtle one. When several states have the same count, nothing determines their relative order, so your output can change between runs on identical data — which is confusing at best and looks like a bug at worst.

And printing a raw `Counter` repr instead of a table. Thirty seconds of f-string alignment is the difference between output that looks dumped and output that looks deliberate.

---

## Drill 3 — Paginate everything

### The stop conditions

Open Brewery DB paginates with `page`, which is **1-based** rather than 0-based, and `per_page`, which maxes out at 200. Crucially, **there is no metadata anywhere telling you the total** — no `count`, no `nbPages`, no `next` link. You find the end by running into it.

Which means two stop conditions, not one:

```python
records = []
for page in range(1, max_pages + 1):
    batch = fetch(page)
    if not batch:
        break
    records.extend(batch)
    if len(batch) < per_page:      # short page = the last one
        break
```

The first catches an empty page. The second catches a **short page** — one that came back with fewer records than you asked for, which can only mean the API ran out. You want both. The short-page check saves exactly one request per full run, which sounds trivial until you remember each request is about a second and you are being watched.

### The cap

`max_pages` is not optional and it is not defensive over-engineering. With no metadata bounding the loop, the only thing standing between you and an infinite sequence of requests is the API behaving precisely as you assumed it would, and that is not something to stake a live interview on. Playbook §4 puts it bluntly: an unbounded `while True` against a misread API is how you send forty thousand requests in front of a stranger. Say the cap out loud when you write it.

### What "caching" means here

Nothing elaborate. Key each response on the pair `(page, per_page)`, write the JSON to a `.cache/` directory, and on the next run check for the file before you check the network. First run hits the API; every rerun after that is instant.

If you skipped this, you burned several minutes of a thirty-minute drill re-waiting on requests you had already made — and you will have felt it, because every small fix to your parsing code cost you the whole fetch again.

### Expect

Roughly 8,000+ breweries across about 40 pages at 200 per page. Two numbers tell you immediately that something went wrong: if you ended with 200 records, your loop ran once and your pagination is broken; if you ended with 50, you never changed `per_page` off its default and the loop was fetching the same small page shape all along.

---

## Drill 4 — Join two sources

### Why this one is hard

The two endpoints describe the same kind of thing and agree on almost nothing about how to describe it:

```
/search.json           -> {"numFound": n, "docs": [ ... ]}
                          docs have: key, title, author_name (a LIST),
                          first_publish_year, edition_count, ...

/subjects/programming.json -> {"name": ..., "work_count": n, "works": [ ... ]}
                          works have: key, title, authors (a list of DICTS),
                          first_publish_year, ...
```

Read that carefully. Both are dict envelopes, but the data lives under `docs` in one and `works` in the other — which is exactly why unit 14 §3 tells you to find the records by shape rather than by name. Same concepts, different key names, different nesting. **And both have list-valued author fields whose elements are different types**: one is a list of plain strings, the other a list of dictionaries you have to reach into for a `name`. That mismatch is the whole exercise.

### The join key

`key` — the Open Library work identifier, which looks like `/works/OL123W`. It is present on both sides and it is the only reliable link between them.

Joining on `title` is tempting and it is wrong. Casing differs, subtitles are present on one side and absent on the other, and punctuation varies. You would get a handful of accidental matches and conclude the overlap is even smaller than it is. This is the same instinct as picking a primary key over a name column in SQL, and it transfers directly.

### The shape of a good answer

Normalise each side into *your* record shape first, separately, and only then join:

```python
search_rows  = [{"key": d["key"], "title": d.get("title"),
                 "authors": d.get("author_name") or [],
                 "year": d.get("first_publish_year"),
                 "editions": d.get("edition_count") or 0}
                for d in search["docs"]]

subject_rows = [{"key": w["key"], "title": w.get("title"),
                 "authors": [a.get("name") for a in (w.get("authors") or [])],
                 "year": w.get("first_publish_year")}
                for w in subject["works"]]

by_key = {r["key"]: r for r in subject_rows}
matched = [r for r in search_rows if r["key"] in by_key]
```

Two things are doing the real work there. The `or []` on both author fields means a missing or null list becomes an empty list rather than `None`, so the loop over it can't explode. And building `by_key` — a dictionary from key to record — turns the join from a nested loop into a lookup, which is both faster and much easier to say out loud: "I'm indexing the subject side by key, then walking the search side and checking membership."

Normalise **both** sides to the same shape before you join. Trying to join the raw responses directly is precisely what makes this drill feel impossible, and it is where most people lose the ten minutes.

### The number that matters

The overlap is usually small — often single digits out of fifty.

**That is the finding.** It is not a failure of your join. The right answer to give is *"these two endpoints surface almost disjoint sets, so the subject listing isn't just a filtered view of search — they're built differently"*, and the wrong answer is *"the join didn't work, let me try matching on title instead."* Reporting both the matched and unmatched counts, as the drill asked, is what lets you tell the difference between an interesting result and a broken one — which is why the drill asked for both.

### If you gave up

That is the most common outcome and it is the reason this drill exists at all. What you are practising here is not the join; it's *narrating a mismatch*. The sentence to have ready is something like: *"these two have different author representations — one's a list of strings, one's a list of objects — so I'm normalising both to a list of name strings before I join."*

Said out loud, that turns a stuck ten minutes into visible, structured problem-solving. Unsaid, the identical ten minutes looks like silence.

---

## Drill 5 — Wrap it in an API

### The skeleton

```python
@app.get("/breweries", response_model=BreweryPage)
async def breweries(
    state: str | None = None,
    brewery_type: str | None = None,
    page: dict = Depends(pagination),
    client: httpx.AsyncClient = Depends(get_client),
):
    ...
```

Everything structural is visible in that signature: the optional query parameters with defaults, pagination pulled in as a dependency so it isn't copy-pasted into every route, the HTTP client injected rather than constructed inside the handler (which is what makes it swappable in a test), and a `response_model` declaring the shape you promise to return.

### What separates a pass from a good pass

**An upstream timeout.** Non-negotiable, every time, no exceptions. Without it a request that never gets answered hangs your service indefinitely, and there is no error to tell you why.

**Error translation.** An upstream 404 becomes your 404; an upstream 5xx becomes your **502**. This distinction is worth understanding rather than memorising: a 500 from your service means *you* are broken, while a 502 — Bad Gateway — means you are working correctly and the thing behind you isn't. They send different people to different dashboards at three in the morning.

**A `response_model`.** The upstream returns fifteen fields; expose the six you actually mean to. Beyond tidiness, this is a boundary — with a response model in place, an upstream schema change cannot silently leak through you to your callers.

**One real test.** `TestClient` plus `dependency_overrides` to substitute a fake upstream. One test that proves you know how to isolate a service from its dependencies is worth more than five tests that hit the live network and fail whenever someone else's server has a bad day.

**A `/health` that does not call upstream.** This one is counterintuitive until you have been burnt by it. A health check exists to report whether *your* process is alive. If it fails when a third party is down, your orchestrator will restart or drain a service that is working perfectly, which makes it worse than having no health check at all.

### Common mistakes

Using `requests` inside an `async def` handler is the classic. `requests` is blocking, so it stops the event loop dead and every other in-flight request waits on it — which defeats the entire point of the handler being async. Either use `httpx.AsyncClient`, or make the handler a plain `def` and let FastAPI run it in a threadpool. Both are correct; the mixture is not.

Passing the raw upstream JSON straight through is the other. It is fast to write and it works, but what you have built is a proxy rather than a service, and you have inherited someone else's schema permanently.

And not opening `/docs`. Open it. It is free, generated for you, and it is immediate evidence about whether your models say what you think they say.

---

## Drill 6 — Full take-home

### The data

`https://api.tvmaze.com/shows?page=0` returns 240 shows. It is nested and it is null-heavy, and it is the most realistic response in this unit for exactly those reasons. Here the field inventory genuinely does read better as a table, because the nesting depth matters as much as the classification:

| Fields | Classification | What to watch for |
|--------|---------------|-------------------|
| `id`, `name`, `type`, `language`, `status` | flat, categorical | the clean ones; group by these freely |
| `genres` | list of strings | one show belongs to several |
| `premiered`, `ended` | temporal (`"2013-06-24"`) | often null |
| `rating.average` | nested numeric | null for a large minority of shows |
| `network.name`, `network.country.code` | nested, 2–3 levels deep | null for web-only shows |
| `webChannel.name` | nested | null for broadcast shows |
| `schedule.time`, `schedule.days` | nested; `days` is a list | |
| `runtime`, `averageRuntime` | numeric | sometimes null |
| `image`, `externals`, `_links`, `summary` | nested / text | you should drop these |

Now the observation that this drill is really built around. **`network` is null exactly when `webChannel` isn't, and vice versa.** They are mutually exclusive: a show is either broadcast or streamed, and the API represents that by nulling out whichever one doesn't apply rather than by giving you a field that says which.

Spotting that and deriving a single `platform` field from the pair — take `network` if it's there, otherwise `webChannel`, and record which one it came from — is the single best move available in this drill. It is the kind of thing that reads as genuine data sense rather than as mechanical flattening, because nothing in the response tells you to do it. You have to notice the pattern in the nulls.

### A good deliverable

Flat records carrying `id, name, type, language, status, genres, premiered_year, rating, platform, platform_country, runtime` — about eleven fields, which is the right order of magnitude. Unit 14 §8's advice applies: five to ten fields, not eighty.

Counts of shows per genre (a list field, so one show counts in several), per language, per status, and per platform type.

For the rating, both the mean and the median — they diverge here, and *saying so* is the point, because a mean well above a median means the distribution is skewed and a few values are pulling it. And the count of shows with no rating at all, **stated explicitly**, because that is a big chunk of the data and quietly excluding it changes the answer.

For time, shows premiered per year, and for shows that have ended, the gap between premiere and end.

Saved: `shows.csv` and `summary.json`. Printed: an aligned report a non-programmer could read.

### The traps

There are five, and every one of them is silent — none raises an error that points at the real problem.

1. **`rating.average` is null for a large minority of shows.** Depending on how you write the average, this either raises inside `mean([...])` or, worse, gets treated as zero by `sum()` and quietly drags your average down. The second failure gives you a plausible wrong number and no warning.
2. **`genres` is a list**, so per-genre counts sum to *more* than the record count. That is correct and it looks wrong. Say it out loud before someone asks, or your totals appear not to add up.
3. **`premiered` is null for unaired shows.** Any year-based bucketing has to decide what to do with them.
4. **`network` versus `webChannel`** — the mutual exclusivity above. Handle only one and you silently lose every show of the other kind.
5. **`summary` contains raw HTML tags.** Either strip them or drop the field entirely; `<p>` markup sitting in a CSV you are presenting is the sort of detail that undoes an otherwise careful piece of work.

### Self-check

If you produced counts per genre and a mean rating and stopped there, that is a **3/5** — correct, and shallow. It is what everyone produces. To get to a 5 you needed at least one of these:

- the network/webChannel unification into a single `platform` field
- mean-versus-median with a comment about the skew
- an explicit missing-data report
- a time trend

And you needed to have said, at the end: *"With more time I'd add X, Y, Z."* That sentence is not optional and it is not modesty. It converts everything you didn't finish from a gap into a demonstration of judgment.

---

## Scoring across all drills

Forget the per-drill rubric for a moment; here is the actual bar. By the time you finish drill 6, can you fetch and inspect an endpoint you have never seen in under two minutes? Do you have clean flat records within ten? Can you produce a readable report by thirty? And did you talk the whole way through?

If yes to those four, you are ready. That is genuinely the bar, and notice how much lower it is than the one you have probably been holding yourself to. It is not "know pandas deeply." It is not "have memorised FastAPI's dependency system." It is speed in the first ten minutes plus honesty about the data, and those two things are most of the score.

---

*The thread running through all six debriefs is one idea: on real data, the thing that goes wrong almost never announces itself. Coordinates arrive as strings and sort into nonsense without raising. A pagination loop stops early and hands you a fifth of the data with total confidence. A null rating gets counted as a zero and pulls your average down. A join returns nine matches and looks broken when it is actually telling you something. Not one of those produces an error message.*

*Which is why every single piece of advice above reduces to the same habit — look at the data before you trust it, count what's missing, and say what you found out loud. You have now practised that six times against endpoints nobody prepared for you. That is the skill. Go and use it.*
