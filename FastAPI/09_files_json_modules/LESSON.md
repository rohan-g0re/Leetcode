# 09 — Files, JSON, and Modules

*This is the last unit of pure-Python plumbing — about twenty-five minutes — and it's where the course stops being practice. Everything up to here worked on data I made up for you. This unit's task works on a genuine, unedited GitHub response sitting in `FastAPI/fixtures/github_repos_pallets.json`: seventeen repository records, eighty-one distinct fields, nulls scattered through it. Nothing is assumed beyond units 01 to 08.*

---

## 1. What this unit is actually for

Picture the interview. Someone gives you a URL, you fetch it, and a wall of JSON comes back. Before you can say anything intelligent about it you have to do three unglamorous things: get it out of wherever it lives and into Python, *look* at it hard enough to understand its shape, and save your results somewhere a human can open. That's this unit.

The middle step is the one people underestimate. Unit 04 told you a parsed JSON response is literally the dictionaries and lists you already know, with no extra layer to learn. True — and still overwhelming the first time you meet a real one, because a real one is eighty-one fields wide and nested three deep. So a good chunk of this lesson is about the tools for *looking* at something like that without drowning in it. By the end you'll take that fixture and produce what unit 04 said to always aim for: a list of flat dictionaries, six clean fields each, nulls handled instead of crashing.

---

## 2. Opening a file, and why you always write `with`

Here is the whole shape of reading a file in Python:

```python
with open("data.txt", "r", encoding="utf-8") as fh:
    text = fh.read()
```

Three ideas are packed into that line. `open()` returns a **file handle** — an object representing your program's live connection to a file on disk. Not the contents; the *connection*. The operating system hands out a limited number of these and expects each one back. `fh` is the conventional name.

The `with` keyword is what hands it back. `with` is Python's **context manager** syntax: a block that guarantees some cleanup runs when the block ends. For a file the cleanup is closing it — and crucially, **it closes even if an exception is raised inside the block.** That connects straight to unit 08. If you write `fh = open(...)` and a `.close()` at the bottom, and something in between raises a `KeyError`, execution leaps out of the function and that `.close()` is never reached: the one path where you most want cleanup is exactly the path that skips it. Think of `with` as a **lease rather than a purchase** — you borrow the file for the indented block, and it goes back however you leave.

The third piece is `encoding="utf-8"`, and on Windows it is not optional. A file on disk is bytes; an encoding is the rulebook for turning bytes into text. If you don't name one, Python asks the operating system, and Windows historically answers with a legacy codepage rather than UTF-8. The consequence is concrete: a name has an accent in it, or a description has a curly quote, and your script dies with `UnicodeDecodeError` — or worse, doesn't die and quietly gives you mangled characters. Your colleague on a Mac runs identical code and it works, which makes it a genuinely confusing bug to report. Pass `encoding="utf-8"` on every `open()` and it never happens.

### The modes

The second argument says what you intend to do:

| Mode | Meaning |
|------|---------|
| `"r"` | read — the default; raises `FileNotFoundError` if the file isn't there |
| `"w"` | write — **truncates an existing file to empty** |
| `"a"` | append — writes go on the end, existing content untouched |
| `"x"` | create — fails if the file already exists |
| `"rb"` / `"wb"` | binary — no encoding argument, and you get `bytes` rather than text |

Mode `"w"` deserves its own sentence. **It empties the file the instant `open()` runs**, before you've written a byte. So if your script opens a file for writing and then crashes while computing what to put in it, you don't have the old file *and* you don't have a new one — you have an empty file where your data used to be. When you want to add to something, `"a"` is the mode, and section 7 is built on it.

---

## 3. Getting text in and out

With a handle open for reading, there are three ways to pull text out, differing in how much they load at once:

```python
text = fh.read()            # the whole file as one string
lines = fh.readlines()      # a list of lines, each with its "\n" still attached
for line in fh:             # one line at a time
    print(line.rstrip("\n"))
```

Looping directly over the handle is the right default: it fetches one line and only reads the next when you ask, so a two-gigabyte log costs you one line of memory rather than two gigabytes. `.read()` is fine for anything small, which includes every fixture here. Lines keep their trailing newline, which is why unit 02's `.rstrip("\n")` appears constantly.

Writing has one trap: `fh.write("line one\n")` does **not** add a newline the way `print()` does, so forget the `\n` and your whole output lands on one enormous line.

---

## 4. `pathlib`, and the script that only works from one folder

Python's older way of handling file locations was gluing strings together: wrong slashes on the wrong operating system, and no way to ask a path a question. The modern replacement is `pathlib`, where **a path is an object with methods rather than a piece of text**.

```python
from pathlib import Path

path = Path("data") / "users.json"
path.exists()
path.parent.mkdir(parents=True, exist_ok=True)
text = path.read_text(encoding="utf-8")
path.suffix         # ".json"
list(Path("data").glob("*.json"))
```

The overloaded `/` is the headline: it builds the correct path with the correct separator on Windows, macOS and Linux alike. `read_text` and `write_text` do the `with open(...)` dance internally — still pass `encoding="utf-8"`, for the reasons above.

Now the idiom that actually matters:

```python
HERE = Path(__file__).parent
data = HERE / "fixtures" / "repos.json"
```

`__file__` is a variable Python sets automatically inside every source file, holding the path to that file itself. So `Path(__file__).parent` is "the folder this code lives in," computed at runtime.

Why bother? Because a plain relative path like `open("fixtures/repos.json")` is not resolved relative to your script — it's resolved relative to the **working directory**, whatever folder the terminal happened to be in when the process started. Your script works when you run it from its own folder and throws `FileNotFoundError` the moment anyone runs it from the project root, or from an IDE, or from a scheduler. That's one of the most common ways a working script mysteriously stops working, and it's why `task.py` opens with `HERE = Path(__file__).parent`. It's also why `load_repos()` can take no arguments at all: `FIXTURES` is anchored to the source file, so `pytest` can invoke it from anywhere and still find the data.

---

## 5. The `json` module — four functions, two pairs

A **module** is a Python file full of ready-made tools, and the **standard library** is the set of modules that ship with Python, no installation needed. `json` is one; you reach it with `import json`.

Its job has a pair of names interviewers use. To **serialize** is to turn a live Python object into text you can store or send; to **deserialize**, also called to **parse**, is the reverse — take text and rebuild the object it describes. Four functions:

```python
import json

json.loads(text)         # JSON string  -> Python object
json.dumps(obj)          # Python object -> JSON string
json.load(file_handle)   # read and parse straight from an open file
json.dump(obj, fh)       # serialize and write straight to an open file
```

The naming trips everybody up once, and the fix is permanent: **the `s` stands for string.** `loads` and `dumps` deal with a string in memory; `load` and `dump`, without the `s`, deal with a file handle. `load` is what goes inside section 2's `with` block; `loads` is what you'll use in unit 12 on the text of an HTTP response.

```python
data = json.loads('{"a": 1, "b": [2, 3]}')     # {'a': 1, 'b': [2, 3]}
```

Look at what came back: a dictionary containing a list. That's unit 04's translation table doing its work — JSON objects become `dict`, arrays become `list`, `null` becomes `None`. There is no special type to learn; parsing hands you the ordinary containers you've used since unit 03.

Against a file, the two halves look like this — essentially the task's `read_json` and `write_json`:

```python
with open(path, encoding="utf-8") as fh:
    data = json.load(fh)

with open(path, "w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2, ensure_ascii=False)
```

Three keyword arguments earn their keep. `indent=2` pretty-prints instead of cramming everything onto one line, and section 6 is about that one. `ensure_ascii=False` keeps `é` as `é` rather than escaping it to `é` — without it your file is valid but unreadable to a human, which is why the task checks that `Zürich` survives as `Zürich`. And `default=str` is the escape hatch for objects JSON has no concept of, most often a `datetime`, which otherwise raises `TypeError: Object of type datetime is not JSON serializable`. It says "anything you can't handle, call `str()` on it" — one argument, a whole class of failure gone.

---

## 6. `json.dumps(obj, indent=2)` — the first minute of the interview

This gets its own section because in practice it's the most valuable line in the unit.

You've just fetched a response and you have *no idea* what's in it. You can't write a useful line of code until you know its shape, and printing it raw gives you an unreadable smear of thousands of characters. So:

```python
print(json.dumps(response_data, indent=2)[:2000])
```

`indent=2` re-renders the structure with each level of nesting pushed two spaces right, so the shape becomes visible at a glance — whether the top level is a list or a dict, what the field names are, where the nested objects sit. Think of it as **turning the lights on** in a room you've just walked into.

The `[:2000]` is the practitioner's half, and it's the part people miss. This unit's fixture is seventeen records of eighty-one fields; pretty-printed that's thousands of lines, and printing all of it blows out your scrollback and teaches you nothing. Two thousand characters is roughly the first record and a bit, which is all you need, because in a well-behaved API every record has the same shape.

Then two follow-ups, in order. `len(data)` tells you how many records you're holding. Then the sorted set of every key appearing across *all* records tells you what you can rely on — that's the task's `repo_field_names`, and it's why that function exists. Records in a real response do not all carry the same keys, which is unit 04's whole argument for `.get()`; this is how you measure the damage before it bites. On this fixture the answer is eighty-one.

---

## 7. When the JSON doesn't parse, and the two output formats

```python
json.loads("not json")
# json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

`JSONDecodeError` is a subclass of `ValueError`, so by unit 08's rule that `except` catches a class and everything beneath it, `except ValueError:` handles it and you needn't recall the exact name under pressure. What's worth knowing is the real cause, which is almost never malformed JSON — it's that the server didn't send JSON at all. It sent an HTML error page, a rate-limit notice, or a login redirect, and you called `.json()` on it. "Line 1 column 1" is Python saying the very first character was wrong, usually a `<`. So build the reflex now: when you see that error, `print(r.text[:300])`, and the answer is sitting there in plain English.

**JSON Lines** (`.jsonl`) is one complete JSON object per line — no wrapping array, no commas. That simplicity is the point:

```python
with open("out.jsonl", "a", encoding="utf-8") as fh:
    fh.write(json.dumps(record) + "\n")
```

Because each record is self-contained, you can **append** with mode `"a"` without reading or rewriting what came before — the one job a plain `.json` file can't do, since a JSON array has to be loaded, appended to, and written back whole every time. Think of JSONL as **a ledger**: you only ever add a line to the bottom. The reason to care arrives in unit 15, when you're paginating through ten thousand records and the connection drops at nine thousand. Accumulating in a list, you have nothing; appending JSONL, you have nine thousand on disk and can resume. Reading it back is a loop parsing each line with `loads`, skipping blanks — trailing blank lines are normal, not an error.

**CSV** is what you produce when a human will open the result in Excel, which is often the answer to "can you send me that?"

```python
import csv

with open("out.csv", "w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=["id", "name"])
    writer.writeheader()
    writer.writerows(rows)

with open("in.csv", newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))
```

`DictWriter` takes exactly unit 04's target shape — a list of flat dictionaries — and `fieldnames` decides both column order and which keys get written: anything in a row that isn't listed is dropped, anything listed but missing from a row comes out empty. `DictReader` is the reverse. Two details you can't skip. `newline=""` is **required**, and omitting it on Windows gives you a blank line between every row, because the csv module writes its own line endings and Python's text layer then translates them again — it looks like a bug in your code and isn't. And `DictReader` gives you **strings for everything**: `row["count"]` is `"42"`, not `42`. CSV has no types, so converting is your job.

---

## 8. Modules, imports, and the file you must not name `json.py`

Every `.py` file is a **module**, and a folder of them is a **package**. Importing runs the module's code once, top to bottom, then caches it — so importing the same thing from five files costs the work once.

```python
import json                       # then write json.dumps(...)
from json import dumps            # then write dumps(...)
from pathlib import Path
```

A reasonable habit: plain `import module` for standard library, because `json.dumps(...)` tells the reader where `dumps` came from, and `from module import name` for the few things you type constantly, `Path` being the obvious one. Never write `from module import *`, which dumps every name that module defines into your **namespace** — the set of names currently visible in your file. You don't know what those names are, and any of them can silently overwrite something of yours.

Which brings us to a trap that costs beginners an afternoon. When you write `import json`, Python searches a list of locations in order, and **your script's own directory comes first**, ahead of the standard library. So a file called `json.py` next to your script gets imported instead of the real thing, and you get `module 'json' has no attribute 'dumps'` — which reads as though Python itself is broken. This is **shadowing**: a name of yours hiding one that already existed, the same phenomenon as unit 01's warning about naming a variable `list` or `sum`. Never name a file after a module you plan to import: not `json.py`, `csv.py`, `types.py`, and above all not `requests.py`, which is the one everybody does in unit 12.

---

## 9. `if __name__ == "__main__":`

```python
def main():
    ...

if __name__ == "__main__":
    main()
```

`__name__` is a variable Python sets automatically in every module it loads — a **nametag** it pins on the file. Run the file directly with `python task.py` and the nametag reads `"__main__"`. Arrive there by being imported from somewhere else and the nametag is the module's own name, `"task"`. So the guard means exactly: *do this only when I am the program being run, not when I am being imported as a library.*

This matters for testability, and this unit's own task is the demonstration. `test_task.py` begins with `from task import load_repos, slim_repos, ...`. Importing runs `task.py` top to bottom, so every statement sitting at the bottom of the file at zero indentation executes as a side effect of that import. Without the guard, running your tests would run your whole script first — and from unit 12 onward, "your whole script" means live network calls. Your tests would be slow, would fail with no internet, and would hammer someone's API every time you pressed enter. With the guard, importing gets you the functions and nothing else.

Every script you write from here on gets this. It also reads well in an interview: it says you understand your file is both a program and a library, and it costs two lines. Anything you want to happen only on a direct run goes inside it — including reading command-line arguments out of `sys.argv`, whose element `0` is the script's own name, so your arguments start at index 1.

---

## 10. Putting it against the real thing

Now open `fixtures/github_repos_pallets.json` and scroll through one record. It's worth thirty seconds of genuine looking, because this is not a tidied-up example: seventeen repositories, eighty-one distinct top-level fields across them, nested objects, and nulls where you'd expect data.

The nulls are the exercise. Two repositories have `"language": null` — GitHub couldn't determine one. Three have `"license": null`, while the rest carry a nested object there with a `"name"` inside it. So the field you want lives at `repo["license"]["name"]` on fourteen records and doesn't exist at all on three.

That's unit 04 section 7's trap arriving for real. `repo["license"]["name"]` raises `TypeError: 'NoneType' object is not subscriptable` the moment it hits one of those three, and — the part that catches people — `repo.get("license").get("name")` fails identically, because the first `.get()` succeeded and returned `None`, and `None` has no methods. The fix is the one you already know:

```python
(repo.get("license") or {}).get("name")
```

Read it as "the licence, or an empty dictionary if that's falsy, then ask *that* for its name." An empty dictionary answers `None` to any key, so the chain ends quietly instead of exploding. Note why `.get("license", {})` isn't enough: a default only fires when the key is **absent**, and here the key is present holding `null`. `or {}` catches both, because `None` is falsy — unit 01's truthiness rules paying rent.

Do that across six fields and you've written `slim_repos`: name, owner pulled up out of the nested owner object, language, stars, forks, licence name. Seventeen flat dictionaries, six keys each, no nesting, no crashes. That is the target shape unit 04 named, produced for the first time out of genuine mess — and once you're standing on it, `language_report` is just counting, which unit 05 already taught you.

---

## 11. What I have deliberately left out

The task needs a couple of things I haven't handed you, and looking things up quickly under mild time pressure is the most transferable skill in this course. So go find these, in the interactive prompt or at docs.python.org.

Start with `Path.mkdir(parents=True, exist_ok=True)` and work out what each flag does on its own — you need both for `write_json`, and knowing why is the point. Then read `json.dumps(..., default=...)` properly, since a `datetime` in your output is a matter of when, not if. Look at `csv.QUOTE_MINIMAL`, or better, write a CSV where one value contains a comma and see what the module does about it. Skim `argparse`, the proper tool for command-line flags and help text that `sys.argv` only gestures at, and glance at `tempfile.NamedTemporaryFile` for scratch space that cleans itself up. Finally, look at `os.environ.get("API_KEY")`: that's how secrets get into a program, you'll need it in unit 13, and hardcoding a key into a file you might commit is the one mistake that can actually cost somebody money.

---

## 12. Check yourself

1. Why use `with open(...)` instead of `open()` plus `.close()`?
2. What does mode `"w"` do to an existing file, and when does it do it?
3. What's the difference between `json.load` and `json.loads`?
4. What does `json.dumps(obj, indent=2)` give you, and when do you reach for it?
5. Why does `if __name__ == "__main__":` matter for testability?
6. What breaks if you name your file `json.py`?

*(Answers: 1. `with` closes the file even when an exception is raised inside the block, and the error path is exactly the path a manual `.close()` gets skipped on. 2. it truncates it to empty — at the moment `open()` runs, before you have written anything. 3. `load` reads from an open file handle; `loads` parses a string already in memory — the `s` is for string. 4. a pretty-printed, indented JSON string; you use it to see the shape of an unfamiliar response, sliced with `[:2000]` so it doesn't flood your terminal. 5. because importing a module runs its whole body, so without the guard your test suite would execute your script, network calls included. 6. Python searches your script's own directory before the standard library, so your file shadows the real `json` module and every `json.dumps` call fails bizarrely.)*

---

*Three things to carry out of this unit. `with open(path, encoding="utf-8")` is the only way you should ever open a file — the `with` guarantees the close even when unit 08's exceptions fire, and the encoding argument is what stops your Windows machine mangling text that works fine on everyone else's. `json.dumps(obj, indent=2)[:2000]` is how you make an unfamiliar response legible, and it is genuinely the first line you'll type when someone hands you a URL. And everything else here serves the goal unit 04 set: get whatever arrives down to a list of flat dictionaries, defending against the nulls on the way, after which the interesting work is easy. Unit 10 adds classes and type hints, and then Part 2 begins — where the JSON stops coming from a file and starts coming down a wire.*

*Now open [`task.py`](task.py).*
