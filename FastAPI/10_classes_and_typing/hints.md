# Unit 10 — hints

*Open this after about ten minutes of genuinely trying a piece — long enough to be stuck on something specific, not long enough to be demoralised. Each section talks through the approach and shows you enough scaffolding to get moving. Nothing here is a finished answer you can paste, and the two class bodies are deliberately left with holes in them.*

---

### `Repo`

The two TODO comments in the class body split the work in half, and it's worth doing them in that order: get the fields right, run the tests, then add the methods.

Fields are just annotated names, one per line. Required ones first, then the ones with defaults, and a field that might legitimately hold nothing gets `| None` in its annotation:

```python
@dataclass
class Repo:
    name: str
    owner: str
    language: str | None = None
    ...
```

Fill in `stars`, `forks`, `license`, and `topics` from the docstring's list. The two counts are whole numbers defaulting to zero. The licence is text or nothing, like `language`.

`topics` is the one that needs thought. Its type is a list of text, so `list[str]`, and its default cannot be written as `[]` — the class would refuse to define itself. Use the `field` function that's already imported at the top of `task.py`, and give it the keyword argument that takes a *callable* — something Python can call to produce a fresh value each time an instance is built. For an empty list, the thing to hand over is `list` itself. Not `list()`: that would call it once, right now, and store the single result, which is the bug you're avoiding.

For the methods, remember `self` is the first parameter of both. `is_popular` is a single comparison against the threshold. `summary` is an f-string, and the "unknown" case is smaller than it looks:

```python
    def summary(self) -> str:
        return f"{self.name} ({self.language or 'unknown'}): {self.stars} stars"
```

`self.language or 'unknown'` works because `None` is falsy — unit 01's truthiness rules doing real work. Note the single quotes inside the double-quoted f-string; nesting the same quote character is a syntax error on older Pythons and a needless risk on newer ones.

You write no `__init__`, no `__repr__`, and no `__eq__`. The decorator generates all three, which is why `Repo(name="a", owner="o") == Repo(name="a", owner="o")` is true without you doing anything.

---

### `repo_from_api`

Every field here is a small defensive expression, and they all follow the same two patterns.

For the nested ones — `owner` and `license` — you have to survive both "the key is missing" and "the key is present holding null." Unit 04's `or {}` handles both in one move, because an absent key gives `None` and a null value gives `None`, and `None` is falsy either way:

```python
owner = (raw.get("owner") or {}).get("login")
license_name = (raw.get("license") or {}).get("name")
```

Read the first one as: get the owner, or an empty dictionary if there wasn't one, then ask *that* for its login. An empty dictionary answers `None` to any key, so the chain ends quietly instead of raising `'NoneType' object is not subscriptable`.

`topics` is the same shape with a different fallback — `raw.get("topics") or []` — and the fixture really does contain a record where topics is null, so this is not hypothetical.

The two counts are the trap most people walk into. `raw.get("stargazers_count", 0)` looks correct and isn't: the default fires only when the key is *absent*, so a key present with a null value still gives you `None`, and `None` lands in a field annotated `int`. Nothing complains — remember that annotations aren't enforced — and the failure surfaces much later when something tries to add up the stars. `raw.get("stargazers_count") or 0` covers both cases.

`language` needs no defence at all. It's allowed to be `None`, `.get` returns `None` when it's missing, and those are the same answer.

Then build and return the `Repo` with those seven values.

---

### `repo_to_dict`

One line, and the function that does it lives in the `dataclasses` module you're already importing from. Its name is a compound of two very ordinary words meaning "as a dictionary." Add it to the import at the top of the file, call it on the repo, return the result.

If you want to confirm before you commit, `import dataclasses; help(dataclasses)` in the interactive prompt lists the whole module, and the function you want is near the top.

---

### `load_repos`

Three steps, none of them new — this is unit 09's file-and-JSON work with unit 07's comprehension on the end.

Build the path from the `FIXTURES` constant already defined at the top of `task.py` rather than writing a relative path, since the tests may run from a different directory. Read the text, parse it, then convert:

```python
path = FIXTURES / "github_repos_pallets.json"
data = json.loads(path.read_text(encoding="utf-8"))
return [repo_from_api(raw) for raw in data]
```

You'll need to add `import json` at the top. Pass `encoding="utf-8"` explicitly — on Windows the default encoding is not UTF-8, and a repository description containing an accent or an emoji will crash the read otherwise.

---

### `ApiClient`

Everything goes under the single TODO at the bottom of the class docstring. Start with the class attribute and the constructor:

```python
class ApiClient:
    DEFAULT_HEADERS = {"Accept": "application/json"}

    def __init__(self, base_url, token=None, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.calls = 0
```

`DEFAULT_HEADERS` sits in the class body, which makes it shared by every instance. The counter sits in `__init__`, which gives every client its own — and a test builds two clients specifically to check that.

`rstrip("/")` is unit 02's string method: it removes trailing slashes if there are any and does nothing if there aren't, so both construction examples in the docstring land on the same stored value.

**`headers()` is the tested part, so slow down here.** The obvious version is wrong in a way that passes two of the three tests:

```python
    def headers(self):
        headers = ???                          # start from DEFAULT_HEADERS
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
```

If you fill that first line with `self.DEFAULT_HEADERS`, you have not made a new dictionary — you've bound a second name to the one dictionary that lives on the class, and the line inside the `if` then writes into it. That's unit 01's "names point at objects" and section 5 of the lesson, together. From that moment on, every `ApiClient` in the program has an `Authorization` header belonging to somebody else's token, including ones created afterwards.

What you want on that line is a *separate* dictionary holding the same pairs. Unit 04 mentioned two ways of getting one: a dictionary method whose name is exactly what it does, and the `dict` constructor, which builds a new dictionary when you hand it an existing one. Either is fine. Then the `if` modifies your copy and the class attribute is never touched — which is what `test_client_headers_does_not_mutate_class_attribute` checks.

`url` takes `*parts`, unit 06's syntax for "however many positional arguments I'm given, collected into a tuple." Start from `self.base_url` and glue each part on with a slash in front of it. Because zero parts means the loop never runs, `client.url()` returns the base URL untouched — no special case needed.

`request` does three things in order: bump `self.calls`, build the URL from the segments it was handed, and return the dictionary the docstring specifies. Note that `path_parts` arrives as a single list, while `url` wants its segments as separate arguments — the star that collected them can also spread them back out, so `self.url(*path_parts)` is the call you want.

`__repr__` returns an f-string matching the expected output exactly, quotes included. The quotes come free from the `!r` conversion:

```python
        return f"ApiClient(base_url={self.base_url!r}, calls={self.calls})"
```

---

### One thing to notice when you're done

Nothing in this task ever checked a type. You annotated `stars: int` and then wrote a defensive `or 0` to keep `None` out of it by hand, because the annotation itself does nothing. Hold onto that feeling of doing the validation manually — in unit 21, Pydantic reads the identical annotation and does all of it for you, and the contrast is the reason this unit came before Part 4 rather than after.
