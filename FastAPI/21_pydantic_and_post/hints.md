# Unit 21 — hints

*Open this after about ten minutes of genuinely trying a piece — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding. The models get shown fairly fully, because they are declarations rather than logic and staring at a blank `class` line teaches you nothing; the endpoints get described rather than written, because that is where the actual work is.*

---

### `WatchIn`

Every line here is a field name, a type, and a default. The only decision is which fields need a `Field(...)` to carry a constraint and which are fine with a bare default.

```python
class WatchIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=100)
    stars: int = Field(default=0, ge=0)
    language: str | None = None
    tags: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, max_length=500)
```

Two things worth reading carefully in that block. `name` and `owner` use `Field(...)` with no `default=`, which is what keeps them *required* — a `Field` carrying only constraints does not give the field a default value. And `tags` uses `default_factory=list` rather than `= []`, so each model gets its own fresh empty list instead of all of them sharing one. That is the trap from unit 06 and unit 10 appearing a third time, and there is a test for it.

The validators are ordinary methods with two decorators stacked above them:

```python
    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        if " " in value:
            raise ValueError("name must not contain spaces")
        return value.lower()
```

The method name is yours to choose; nothing depends on it. What matters is the string in `@field_validator("name")`, which names the field, and the fact that both branches do the right thing: `raise` to reject, `return` to accept the transformed value.

For `tags` you want lowercased, stripped, de-duplicated, and sorted. Three of those four fall out of one set comprehension plus `sorted`:

```python
    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value):
        cleaned = {tag.strip().lower() for tag in value if tag and tag.strip()}
        return sorted(cleaned)
```

Building a `set` does the de-duplication for you, and `sorted` turns it back into a list in a deterministic order — unit 03's exact reasoning about why you never return a bare set. The `if tag and tag.strip()` filter is what drops the empty and whitespace-only tags before they reach the set.

Both validators **return**. That is the part people forget, and forgetting it sets the field to `None` without any error at all.

---

### `WatchOut`

Seven plain fields and no validators. `id`, `name`, `owner`, `stars`, `language`, `tags`, `full_name`.

`full_name: str` is an ordinary required field of type `str`. It looks like it ought to be special because it is derived rather than stored, but from the model's point of view it is just a string that has to be present in whatever the endpoint returns. `to_out` is what computes it.

Set defaults the way you would expect — `language: str | None = None`, `tags` with a `default_factory` — and give `id`, `name`, `owner`, `stars` and `full_name` no default, since a response is never allowed to be missing them.

Do not add `notes`. That is the whole point of the class.

---

### `WatchPatch`

Four fields, every one of them optional, which here means every one has a `None` default and a type that permits `None`.

The thing to get right is that optional does not mean unconstrained. `stars: int | None = Field(default=None, ge=0)` still rejects `-5`, because `ge=0` applies to any value actually supplied. Same for `notes` and its `max_length=500`.

---

### `WatchStats`

Five fields, straight off the docstring. The only line worth a second look is `top: WatchOut | None = None` — a model used as the type of a field inside another model. That is all nesting is, and it means the entry you put in `top` gets validated and filtered like any other `WatchOut`, which is why `notes` cannot escape through this endpoint either.

`languages: dict[str, int]` wants a `default_factory=dict` for the same reason `tags` wanted `default_factory=list`.

---

### `to_out`

Return a dict with the seven keys `WatchOut` declares, reading each one out of the stored record and building `full_name` with an f-string:

```python
        "full_name": f"{stored['owner']}/{stored['name']}",
```

Watch the quoting there — the f-string is in double quotes, so the dictionary keys inside the braces use single quotes.

Use `stored.get("language")` and `stored.get("tags", [])` rather than square brackets for the two fields that might not be present, which is unit 04's habit paying rent. Returning a dict rather than a `WatchOut` instance is deliberate and fine: `response_model` validates whatever you hand back.

You will also want a small ranking helper, since two endpoints need the same order:

```python
def _ranked(records):
    return sorted(records, key=lambda r: (-r["stars"], r["name"]))
```

That is unit 07's tuple key: negate the number you want descending, leave the one you want ascending alone, and you get both in a single sort.

---

### `POST /watch`

The decorator carries three things — the path, `response_model=WatchOut`, and `status_code=201`. The function takes one parameter annotated with `WatchIn`, which is what tells FastAPI the data comes from the body.

Do the conflict check first, before you call `_new_id()`, so a rejected request does not consume an id. Loop over `_STORE.values()` comparing `(owner.lower(), name.lower())` against the incoming pair, and on a match:

```python
        raise HTTPException(
            status_code=409,
            detail=f"already watching: {item.owner}/{item.name}",
        )
```

Then three lines for the happy path: `stored = item.model_dump()` to get a plain dict, `stored["id"] = _new_id()`, and put it in `_STORE` under that id. Return `to_out(stored)`.

Note what `model_dump()` gets you — the *whole* record, `notes` included. That is intentional. The store keeps everything and `response_model` strips `notes` on the way out, which is the in-model/out-model split doing its job with no work from you.

---

### `GET /watch`

Three query parameters. `language` is a plain `str | None = None` with no constraints. The other two need `Query` to carry theirs:

```python
    min_stars: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
```

Start from `list(_STORE.values())` and narrow it. For the language filter, lowercase both sides, and use `(record.get("language") or "").lower()` on the stored side so a record with no language does not blow up on `None.lower()` — unit 04's `or {}` pattern with an empty string instead of an empty dict.

Then rank and slice and convert, which is one line:

```python
    return [to_out(record) for record in _ranked(matches)[:limit]]
```

The slice comes after the sort. Slicing first would give you an arbitrary N rather than the top N, and the tests would not notice on small data — but a reviewer would.

---

### `GET /watch/{item_id}`

Four lines. `_STORE.get(item_id)`, and if that is `None`, raise `HTTPException(status_code=404, detail=f"not found: {item_id}")`. Otherwise `return to_out(stored)`.

Use `.get()` rather than square brackets so a missing id gives you `None` to test rather than a `KeyError` you have to catch. And notice you never check that `item_id` is a number — the `int` annotation already did that, and `/watch/abc` was rejected with a 422 before your function was reached.

---

### `PATCH /watch/{item_id}`

Look the record up and 404 exactly as the GET does. Then the entire update is one line:

```python
    stored.update(patch.model_dump(<the argument you looked up>))
```

That argument is the whole exercise, and section 10 of the lesson told you what problem it solves. It makes the dump contain only the fields that were actually present in the request, so an omitted `language` never appears in the dump and therefore never overwrites anything, while an explicit `"language": null` does appear, as `None`, and correctly clears the stored value. Without it, every field the caller left out would be dumped as `None` and would wipe good data.

Then `return to_out(stored)`. `stored` is the dict living in `_STORE`, so updating it in place has already saved the change — unit 01's "names point at objects" being genuinely convenient for once.

---

### `DELETE /watch/{item_id}`

`status_code=204` on the decorator. Check membership with `if item_id not in _STORE:` and 404 with the same detail string as the others. Otherwise `del _STORE[item_id]` and return nothing at all.

Returning nothing is enough in current FastAPI versions, and the test only asserts that the status is 204 and the body is `b""`. If you want to be explicit about it you can import `Response` from `fastapi` and return `Response(status_code=204)`, which says what it means and works on every version.

---

### `GET /watch-stats`

Guard the empty store first and return the all-zero shape literally:

```python
        return {
            "count": 0,
            "total_stars": 0,
            "mean_stars": None,
            "languages": {},
            "top": None,
        }
```

`response_model` validates this too, so those five keys must match `WatchStats` exactly — a typo here is a 500 rather than a wrong answer, which is the error-you-want.

For the populated case, build the language counts with the ordinary counting loop from unit 04, keying on `record.get("language") or "unknown"` so that both a missing language and an explicit `None` land in the same bucket. Sum the stars, divide by the count, and `round(..., 2)` for the two decimal places. For `top`, reuse `_ranked` and take the first: `to_out(_ranked(records)[0])`.
