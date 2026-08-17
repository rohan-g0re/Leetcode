# Unit 20 — hints

*Open this once you have genuinely tried a route for ten minutes or so — long enough to be stuck on something specific, not long enough to be fed up. Each section explains the approach and gives you partial scaffolding. None of them hands you a finished endpoint.*

---

### The shape every route has

Before anything else, get this shape in your fingers, because all seven routes are the same shape and only the middle changes.

```python
@app.get("/health")
def health():
    return {"status": "ok", "repos": len(REPOS)}
```

A decorator naming the method and the path, a plain `def` underneath, and a `return` of a dictionary or a list. That is the whole vocabulary. There is no serializer to call, no response object to build, and no `json.dumps` anywhere — you return Python and FastAPI sends JSON.

Start with `/health` even though it looks trivial. It proves your imports, your `app` object, your decorator, and your test setup all work, so that when the next route misbehaves you know the problem is in the next route.

### Write the sort once

Four of the routes need repositories in the same order: most stars first, and ties broken alphabetically by name. Write that once and call it everywhere, rather than typing the same `sorted` four times and getting one of them slightly different.

```python
def _ranked(repos):
    return sorted(repos, key=lambda r: (-r["stars"], r["name"]))
```

That's unit 07's tuple-key trick. Python compares tuples element by element, so the key gives you a primary sort and a tiebreaker in one pass, and negating the star count turns ascending into descending on that field alone while leaving the name ascending. The leading underscore in the name is a convention meaning "this is an internal helper, not part of the API" — it stops anyone wondering whether it's an endpoint.

---

### `/repos`

Almost all of the difficulty in this route is in the signature, so get that written down first and the body becomes straightforward.

```python
@app.get("/repos")
def list_repos(
    language: str | None = None,
    min_stars: int = Query(default=0, ge=0),
    archived: bool | None = None,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
```

None of those names appear in the path `/repos`, so all five are query parameters. Every one has a default, so every one is optional. The `ge` and `le` bounds are what produce the 422s the tests demand for `limit=0`, `limit=101`, `limit=-1`, `offset=-1`, and `min_stars=-5`; the sixth case, `limit=many`, is caught by the `int` annotation alone, before the bounds are even consulted. You write no validation code for any of them.

For the body, filter step by step, rebinding the same variable each time so the filters stack:

```python
matches = REPOS
if language is not None:
    ...
```

Then rank the survivors, and take the page with a slice:

```python
ranked = _ranked(matches)
page = ranked[offset : offset + limit]
```

Two details in that slice are doing real work. It comes *after* the ranking, which is what makes the pages line up with the global order rather than each page being sorted only within itself. And slicing past the end of a list gives you an empty list rather than raising, so the "offset past the end" test needs no special case from you — `ranked[100:110]` on a seventeen-item list is simply `[]`.

Then build the response, remembering that `total` is `len(ranked)` and `count` is `len(page)`. Those are the two different numbers the specification insists on: matches before paging, versus rows actually handed over.

**The one that catches people** is `archived`. Write `if archived:` and a request for `archived=False` takes the same branch as a request that never mentioned archived at all, because `False` and `None` are both falsy — unit 01's truthiness trap, in a place where it genuinely matters. Test against `None` explicitly:

```python
if archived is not None:
    matches = [r for r in matches if r["archived"] is archived]
```

For `language`, remember that a repo's language can be `None`, so lowercase it defensively — `(r["language"] or "").lower()` — rather than calling `.lower()` on something that might be nothing. That's unit 04's `or {}` pattern with a string instead of a dictionary.

---

### `/repos/top`

**Declare this above `/repos/{name}` in the file.** That is the entire difficulty of this route.

Routes are matched in the order they were declared, first match wins. Declared the other way round, a request for `/repos/top` matches `/repos/{name}` first, FastAPI calls your lookup handler with `name="top"`, no repository is called that, and you get a 404 from a route that reads perfectly well. If the test named `test_repos_top_is_not_shadowed_by_name_route` fails, do not go looking at your ranking code — move the function.

The body itself is one line: rank all the repos and slice off the first `n`. The parameter is `n: int = Query(default=3, ge=1, le=20)`, which handles the `n=0`, `n=21`, and `n=-1` rejections for you.

Return the list itself, with no wrapper dictionary around it — the test asserts the body is a list.

---

### `/repos/{name}`

`name` appears in braces in the path, so FastAPI fills it from the URL segment. Declare it as a plain `name: str` parameter and nothing else is needed.

Lowercase what you were given once, before the loop, then walk `REPOS` comparing lowercased names and `return` the moment you find one. If the loop finishes without returning, there was no match:

```python
raise HTTPException(status_code=404, detail=f"repo not found: {name}")
```

Two things to get right. **Raise it, don't return it** — returning an `HTTPException` sends it as a normal body with status 200, and your 404 test will fail with a confusing message about the status being 200. And put the name the caller asked for into the detail string, unchanged, not the lowercased version; the test looks for the original text inside the detail.

The `raise` also means you don't need an `else` or a flag variable. Raising ends the request there and then, so anything after the loop is unreachable by design.

---

### `/languages`

This is a group-by, and the tool is unit 04's `setdefault`. Walk the repos once, accumulating into a dictionary keyed by language name:

```python
totals = {}
for repo in REPOS:
    key = repo["language"] or "unknown"
    entry = totals.setdefault(key, {"language": key, "repos": 0, "total_stars": 0})
    entry["repos"] += 1
    entry["total_stars"] += repo["stars"]
```

`setdefault` returns the existing entry if the key is there and inserts your starter dictionary and returns *that* if it isn't, which is why one line handles both the first repository of a language and the fortieth. Note that the starter dictionary carries the language name inside it as well as being keyed by it — that saves you rebuilding the entries later, because the values are already exactly the shape the response wants.

`repo["language"] or "unknown"` is what puts the language-less repositories in their own bucket instead of under a `None` key. This matters for more than tidiness: one test checks that the per-language repo counts still add up to 17, which they only do if nothing was dropped.

Then sort the collected entries and return them:

```python
return sorted(totals.values(), key=lambda e: (-e["total_stars"], e["language"]))
```

`sorted` is what turns `totals.values()` into a real list. Returning `.values()` directly would hand FastAPI a `dict_values` object, which it does not know how to serialize — a list is fine, that particular view object is not.

---

### `/stats`

No parameters, one dictionary out. The interesting part is that four of the seven values are counts of "repos where some condition holds," and there is one idiom for all of them:

```python
sum(1 for r in REPOS if r["archived"])
```

That produces a `1` for each repository that passes and adds them up, which is counting without building an intermediate list. Same shape for `licensed`, using `r["license"]` as the condition — a repository with no licence has `None` there, which is falsy, so no explicit `is None` check is needed for a plain count.

For distinct languages, build a set and take its length, filtering out the `None`s as you go:

```python
len({r["language"] for r in REPOS if r["language"]})
```

That deliberately excludes the language-less repositories, which is why this number is one smaller than the number of entries `/languages` returns.

Mean and median come from the standard library rather than by hand:

```python
import statistics as st
st.mean(stars)
st.median(stars)
```

Round both to two decimal places as the specification asks. The median happens to come out a whole number here, which is fine — `round(167, 2)` is still `167`, and that is what the test expects.

Guard the empty case if you like (`if stars else None`); it cannot happen with this fixture, but it costs one conditional and it is the reflex from unit 01 that stops a divide-by-zero on real data.

---

### `/search`

The whole validation story is one parameter declaration:

```python
q: str = Query(min_length=2, max_length=50)
```

No `default=`, so `q` is required, so a request without it is a 422. `min_length=2` rejects `q=a`. `max_length=50` rejects a fifty-one character string. That is all three cases the test checks, from one line, with error messages you did not write and constraints that show up in `/docs`. This is the point in the task where the framework most obviously earns its keep — compare it against `validate_page_size` in unit 08.

The body is a substring filter, lowercasing both sides so the match is case-insensitive:

```python
needle = q.lower()
items = [r for r in REPOS if needle in r["name"].lower()]
```

Then return `{"q": q, "count": len(items), "items": items}`, echoing back `q` exactly as it was given rather than the lowercased version. Zero matches is a normal 200 with `count` 0 and an empty list, not a 404 — a search that found nothing succeeded at searching.

Nothing specifies an order for the results, but running them through `_ranked` costs you nothing and makes the output reproducible, which is worth doing on principle.

---

### When something is failing and you cannot see why

Two moves, in this order.

Run the single failing test with `-v` and read the assertion rather than skimming it; the tests here compare whole dictionaries, so the diff usually names the exact key that is wrong.

Then start the server with `uvicorn task:app --reload` and open `http://127.0.0.1:8000/docs`. The endpoint list on that page is in declaration order, which makes the `/repos/top` shadowing problem visible immediately, and "Try it out" lets you fire the exact request the test is firing and look at the real response. Two minutes there beats twenty minutes of guessing.
