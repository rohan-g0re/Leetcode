# Part 0 — Setup

30 minutes. Do not skip. Do not read Part 1 until the last command on this page works.

---

## 0.1 What Python actually is (60 seconds)

Python is two things and conflating them causes most beginner confusion:

1. **The language** — the syntax rules you write.
2. **The interpreter** — a program named `python` (or `python.exe`) that reads your `.py`
   text file, line by line, and does what it says.

There is no compile step you invoke, no build artifact. You write `hello.py`, you run
`python hello.py`, the interpreter executes it top to bottom and exits. That's the whole
model.

A **package** (also called a library or module) is Python code someone else wrote that you
install and then `import`. `requests`, `pandas`, and `fastapi` are packages. They are not
part of Python; you install them.

**pip** is the tool that installs packages. It downloads them from PyPI (the Python Package
Index, a public registry) and drops them into a folder your interpreter searches when you
write `import`.

---

## 0.2 Confirm Python

Open PowerShell in this folder and run:

```powershell
python --version
```

You should see `Python 3.11.9` (anything 3.10+ is fine for this course).

Now check pip:

```powershell
python -m pip --version
```

> **Note for this machine specifically:** the bare `pip` command is broken here — its
> launcher points at a stale path and errors with
> `Fatal error in launcher: Unable to create process...`. **Always use `python -m pip`
> instead of `pip`.** They do exactly the same thing; `python -m pip` just tells your
> known-good interpreter to run the pip module directly, bypassing the broken shortcut.
> This is a genuinely useful habit anyway — on machines with several Python versions,
> `python -m pip` guarantees you install into *the interpreter you're actually running*.

---

## 0.3 Virtual environments — what and why

If you `python -m pip install pandas` globally, that version of pandas is now shared by
every project on your machine. Project A needs pandas 1.5, project B needs 2.2 — you're
stuck. Worse, you can't tell a colleague what your project actually needs, because your
global site-packages is a junk drawer accumulated over years.

A **virtual environment** ("venv") is a self-contained folder holding its own copy of the
interpreter's linkage and its own `site-packages` directory. **Activating** it changes what
the words `python` and `pip` point to in your current shell session. Deactivate (or close
the terminal) and everything reverts.

Create one at the root of this course folder:

```powershell
cd C:\Users\rohan\Desktop\Work\STUFF\Projects\Leetcode_Fall_2025\FastAPI
python -m venv .venv
```

That creates a `.venv\` folder. Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Your prompt should now be prefixed with `(.venv)`. That prefix is the *only* reliable
signal that the venv is active. Every time you open a new terminal, you must activate again.

### If PowerShell refuses with an execution policy error

Windows blocks unsigned scripts by default. Fix it for your user only (safe, does not
require admin, does not weaken system-wide policy):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then retry the activate command. `RemoteSigned` means: locally-created scripts run;
scripts downloaded from the internet must be signed.

### Verify the venv is really in charge

```powershell
(Get-Command python).Source
```

It must print a path ending in `...\FastAPI\.venv\Scripts\python.exe`. If it prints a
system path, the venv is not active and you will install packages into the wrong place.

To leave the venv later: `deactivate`.

---

## 0.4 Install the packages

With `(.venv)` showing:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

What you just installed and why:

| Package | Why it's here |
|---------|---------------|
| `requests` | The standard, blocking HTTP client. How you call an API in three lines. Parts 2–3. |
| `httpx` | Modern HTTP client. Same API as `requests` but also supports `async`. Part 4. |
| `pandas` | Tabular data: filtering, grouping, joining, stats. Part 3. |
| `fastapi` | The web framework you'll build APIs with. Part 4. |
| `uvicorn` | The server that actually runs a FastAPI app and listens on a port. Part 4. |
| `pydantic` | Data validation via type hints. FastAPI's engine; installed as its dependency. |
| `pytest` | Test runner. Every task in this course is checked by pytest. |
| `python-dateutil` | Flexible date parsing. Real APIs return dates in inconsistent formats. |

> **Why plain `uvicorn` and not `uvicorn[standard]`:** the `[standard]` extra pulls in
> `httptools` and `uvloop`, which need a C compiler on Windows and fail to build on this
> machine. They are pure speed optimizations — everything in this course works identically
> without them. If you see `Failed to build installable wheels for httptools`, this is why,
> and you can ignore it.

Confirm:

```powershell
python -m pytest --version
```

If that prints a version number, you are set up. **Do not proceed until it does.**

---

## 0.5 Running Python code — the four ways

You'll use all four. Know which is which.

### 1. A script file

Make `scratch.py` anywhere:

```python
print("hello")
```

```powershell
python scratch.py
```

The interpreter reads the file top to bottom, executes each statement, exits. This is how
you run real programs.

### 2. The REPL (interactive)

```powershell
python
```

You get a `>>>` prompt. Type an expression, hit enter, see the result immediately:

```
>>> 2 + 2
4
>>> "abc".upper()
'ABC'
```

Exit with `exit()` or Ctrl+Z then Enter (Windows).

**The REPL is your most important learning tool and most people underuse it.** When you
don't know what a value looks like, don't guess and don't reason about it abstractly —
paste it into the REPL and look. In an interview, poking at an unfamiliar API response in
a REPL (or a notebook cell) is normal, expected professional behavior, not a confession
of ignorance.

Two REPL commands worth memorizing right now:

```python
>>> type(x)      # what kind of thing is x?
>>> dir(x)       # what can I do to x? (lists every attribute and method)
>>> help(x.foo)  # what does that method actually do?
```

Those three get you unstuck without leaving the terminal.

### 3. `-c` for a one-liner

```powershell
python -c "import requests; print(requests.get('https://api.github.com').status_code)"
```

Handy for quick checks without creating a file.

### 4. pytest

```powershell
python -m pytest test_task.py -v
```

pytest finds every function named `test_*` in the file, runs it, and reports pass/fail.
`-v` ("verbose") lists each test by name instead of printing dots.

Other flags you'll want:

```powershell
python -m pytest test_task.py -v -x          # stop at the first failure
python -m pytest test_task.py -k "median"    # run only tests whose name contains "median"
python -m pytest -v -m "not live"            # skip tests that need the internet
python -m pytest test_task.py -v -s          # don't swallow print() output
```

That last one matters: pytest captures `print()` by default, so your debug prints seem to
vanish. `-s` shows them.

---

## 0.6 Reading an error (the single most valuable 3 minutes here)

You will see this constantly. Learn to read it *now* rather than panicking at it later.

```
Traceback (most recent call last):
  File "C:\...\task.py", line 12, in <module>
    print(total(data))
          ^^^^^^^^^^^
  File "C:\...\task.py", line 8, in total
    return sum(row["value"] for row in rows)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'value'
```

Read it **bottom-up**:

- **Last line is the actual error.** `KeyError: 'value'` — a dictionary was asked for the
  key `'value'` and doesn't have it.
- **The frame directly above the last line is where it blew up:** `task.py` line 8,
  inside the function `total`.
- **Frames above that are the call chain** that got you there: line 12 called `total`.

"Traceback (most recent call last)" is telling you the order: oldest call at the top, the
place it actually exploded at the bottom. Nearly everyone reads it top-down at first,
sees library internals, and concludes the library is broken. It almost never is. Start at
the bottom.

The five errors you'll hit most in this course, and what each means:

| Error | It means |
|-------|----------|
| `NameError: name 'x' is not defined` | You used a variable/function you never created — or typo'd the name. |
| `TypeError: ... ` | Right name, wrong kind of value. E.g. adding a string to an integer. |
| `KeyError: 'foo'` | Dict has no key `'foo'`. Extremely common with API responses. |
| `IndexError: list index out of range` | Asked for item 5 of a 3-item list. |
| `AttributeError: 'NoneType' object has no attribute 'x'` | Something returned `None` (usually a function that fell off the end, or a failed lookup) and you used it as if it were real. |

---

## 0.7 Editor

You're in VS Code already. Two things worth doing:

1. Install the **Python** extension (Microsoft). Gives you syntax highlighting, error
   squiggles, and go-to-definition.
2. Point VS Code at your venv: `Ctrl+Shift+P` → "Python: Select Interpreter" → choose the
   one under `.venv`. Without this, VS Code will red-underline `import requests` even
   though it works fine in the terminal.

---

## 0.8 Sanity check

Run this. It exercises Python itself, a package, and a real network call.

```powershell
python -c "import requests, pandas, fastapi; r = requests.get('https://api.github.com/users/torvalds', timeout=10); print(r.status_code, r.json()['public_repos'])"
```

Expected: `200` followed by a number.

If you got that: everything is installed, and **you just made your first real API call.**
That is the entire interview task in miniature — request a URL, check the status, read a
field out of the JSON. The rest of this course is understanding every word of that line
and knowing what to do when it goes wrong.

→ Next: [`01_values_and_types/LESSON.md`](01_values_and_types/LESSON.md)
