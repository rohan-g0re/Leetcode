# Unit 09 — hints

*Open this after about ten minutes of genuinely trying a function — long enough to be stuck on something specific, not long enough to be demoralised. Each section explains the approach and gives you partial scaffolding; none of them hands you a finished function.*

---

### `read_json`

Two problems to solve, and they come apart neatly. The first is that `path` might be a string or might be a `Path` object, and you need one piece of code that copes with either. The fix is a single character of effort: `Path(path)`. Wrapping something in `Path()` that is already a `Path` gives you an equivalent `Path` back, so it is safe to do unconditionally and you never have to check which kind you were handed. Get into the habit of writing that line first in any function that takes a path.

The second is actually reading and parsing. `Path` objects have a `read_text` method that does the whole `with open(...)` dance for you internally, so this comes down to reading the text and then parsing it:

```python
path = Path(path)
text = path.read_text(encoding="utf-8")
return json.loads(text)
```

Remember the naming rule from the lesson: the `s` in `loads` stands for **string**. You have a string in your hand here, so `loads` is right. `json.load` without the `s` wants an open file handle instead, and you would get it if you wrote the `with open(...)` version — both are correct, this one is just shorter.

Notice there is no `try`/`except` anywhere in this function, and that is the point. If the file is missing, `read_text` raises `FileNotFoundError` and it travels straight up to whoever called you. Doing nothing is the implementation of "let it propagate".

---

### `write_json`

The mkdir line is the one people leave out, so put it in before anything else. `parents=True` means "make every missing folder in the chain, not just the last one", and `exist_ok=True` means "if it is already there, that is fine, do not raise". You want both, because without the first a two-deep path still fails, and without the second the function breaks the second time you call it.

```python
path = Path(path)
path.parent.mkdir(parents=True, exist_ok=True)
```

`path.parent` is the folder containing the file — you are creating the directory, not the file, so the `.parent` matters.

Then serialize and write in one go. The two keyword arguments in this call are both being tested:

```python
path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
return path
```

`indent=2` is what puts newlines in the output, which is what the "should be indented, not one line" test is checking for. `ensure_ascii=False` is what keeps `Zürich` as `Zürich` instead of turning it into `Zürich` — the name reads backwards, so remember it as "do not force everything down into plain ASCII". And `encoding="utf-8"` on the `write_text` call is separate from `ensure_ascii`: one decides what characters go into the string, the other decides how those characters become bytes on disk. You need both.

---

### `read_jsonl`

Take the missing-file case first and get it out of the way, because everything after it can then assume the file is there:

```python
path = Path(path)
if not path.exists():
    return []
```

For the rest, read the whole file and split it into lines. `.splitlines()` is the method you want because, unlike `.readlines()`, it strips the trailing newline off each line for you — and `json.loads` would cope with the newline anyway, but a line that is *only* a newline becomes an empty string, which is much easier to spot and skip:

```python
out = []
for line in path.read_text(encoding="utf-8").splitlines():
    if line.strip():
        out.append(json.loads(line))
return out
```

`if line.strip():` is the blank-line skip. `.strip()` removes surrounding whitespace, and an empty string is falsy, so a line that is blank or nothing but spaces fails the test and is silently passed over. That is unit 01's truthiness rules doing real work — you are not comparing to `""`, you are just asking whether anything is left.

---

### `append_jsonl`

Mode `"a"` is the entire idea. It opens the file for writing without truncating it, positions you at the end, and creates the file if it is not there — so all three of your requirements are handled by one character:

```python
with open(path, "a", encoding="utf-8") as fh:
    fh.write(json.dumps(record) + "\n")
```

The `+ "\n"` is not optional. `fh.write` does not add a newline the way `print` does, so leaving it off means your second record lands on the same line as the first, and now neither of them parses. That is the classic JSONL bug and it is invisible until you try to read the file back.

For the return value, do not count lines by hand — call your own `read_jsonl` and take its length:

```python
return len(read_jsonl(path))
```

This is worth doing deliberately rather than out of laziness. It means the count you report is the count somebody actually reading the file would get, so if your writing and your reading ever disagreed, this line would catch it.

---

### `write_csv`

Start with the same two lines as `write_json` — wrap the path, make the parent directory. Then resolve `fieldnames` before you open anything, because the empty-list behaviour depends on it:

```python
if fieldnames is None:
    fieldnames = list(rows[0].keys()) if rows else []
```

The `if rows else []` guard is there because `rows[0]` on an empty list raises `IndexError`. When you have neither fieldnames nor rows, you end up with an empty list of columns, and that is exactly what produces the empty file the spec asks for.

Now the write itself. Note `newline=""` on the `open`, and `extrasaction="ignore"` on the writer:

```python
with open(path, "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
    if fieldnames:
        writer.writeheader()
    writer.writerows(rows)
return len(rows)
```

`extrasaction="ignore"` is what stops `DictWriter` raising `ValueError: dict contains fields not in fieldnames` when it meets the test row carrying an unexpected `extra` key. The default is to raise, which is the wrong default for messy real data. The reverse case — a name in `fieldnames` that a row does not have — needs no argument at all, because `DictWriter` already writes an empty cell for it.

`if fieldnames:` is what makes the two empty-list cases differ. With columns known you write the header and then `writerows([])` adds nothing, giving you a header-only file; with no columns you skip the header too and the file comes out empty. And `csv` needs importing at the top of the file alongside `json`.

---

### `load_repos`

One line. `FIXTURES` is already a `Path`, so `/` joins the filename onto it with the right separator for whatever machine this runs on, and `read_json` takes it from there:

```python
return read_json(FIXTURES / "github_repos_pallets.json")
```

If this raises `FileNotFoundError`, print `FIXTURES` and look at what you actually got — that is faster than guessing, and it is the same debugging move you will use every time a path is wrong.

---

### `repo_field_names`

A set with a union in a loop. Start empty, and for each record fold in that record's keys:

```python
names = set()
for repo in repos:
    names |= set(repo.keys())
return sorted(names)
```

`|=` is the set union assignment — "add everything in the right-hand set that is not already in mine". `names.update(repo.keys())` does exactly the same thing and reads more plainly if the operator is unfamiliar; pick whichever you will still understand in a month.

The set is what makes this correct rather than just convenient: `name` appears in all seventeen records and you want it once, and a set gives you that for free without a single `if x not in` check. Then `sorted()` turns the set into a list in alphabetical order, which is both what the spec asks for and what makes the output readable when you print it.

---

### `slim_repos`

Loop over `repos`, build a fresh six-key dictionary for each one, append it to a list. Five of the fields are plain lookups; write those first and get the shape right before you worry about the licence.

The licence needs two lines, and they are the two lines this whole unit has been building towards:

```python
license_info = repo.get("license") or {}
license_name = license_info.get("name")
```

The first line reads as "the licence, or an empty dictionary if that was falsy". When the record has a real licence object, `or` leaves it alone and `license_info` is that dictionary. When the record has `null`, Python sees `None`, which is falsy, so `or` hands you `{}` instead. Either way the second line is now asking a dictionary for a key, which is always safe — an empty dictionary just answers `None`.

It is worth being clear about why `repo.get("license", {})` does *not* work here, because it looks like it should. A default argument only fires when the key is **missing**. In this fixture the key is present on every single record; it simply holds `null` on three of them. So `.get` finds the key, returns the `None` it found, ignores your default entirely, and the next `.get` call blows up on `None`. `or {}` catches both situations because it tests the *value* rather than the key's existence — and that distinction is the reason this particular fixture is in the course.

`language` is easier: `repo["language"]` may be `None` and you keep it as `None`, no defending required. `owner` is the nested one, `repo["owner"]["login"]`, and that one is safe to index directly because every record has an owner.

---

### `language_report`

Run `slim_repos` first and then everything is arithmetic over clean, flat records:

```python
slim = slim_repos(repos)
```

For the counts, use unit 05's dictionary-counting pattern, converting `None` to `"unknown"` on the way in:

```python
languages = {}
for r in slim:
    key = r["language"] or "unknown"
    languages[key] = languages.get(key, 0) + 1
```

`languages.get(key, 0) + 1` is the whole trick: it reads the current count, or `0` if this is the first time you have seen this language, and stores one more. That avoids the `KeyError` you would get from `languages[key] + 1` on a new key. `setdefault` does the same job if you prefer it.

`total_repos` is `len(slim)` and `total_stars` is a running sum, or `sum(r["stars"] for r in slim)` if you have met unit 07's comprehensions. `top_repo` is a sort with a tuple key, the same shape as unit 03's `top_n`:

```python
top_repo = sorted(slim, key=lambda r: (-r["stars"], r["name"]))[0]["name"]
```

Negating the stars makes the biggest count sort first, since ascending order on negative numbers is descending order on the originals. The name stays un-negated, so two repos with identical star counts fall back to alphabetical order — which is the tie rule the docstring asks for. Then `[0]` takes the winner and `["name"]` pulls out just its name.
