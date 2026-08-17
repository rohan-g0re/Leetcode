# 02 — Text

*Twelve minutes of reading, then the task. This follows directly on from unit 01 and assumes nothing beyond it. Everything about text that this course will ever need is here.*

---

## 1. Why an entire lesson on text

It's tempting to treat text as the boring type — the one you already understand because you've been reading it your whole life. That instinct is wrong here, and here's why.

Every response from every API arrives as **text first**. Before Python turns it into numbers and records, it is one long string of characters. And even after that conversion, look at what's left: the field names are text, the IDs are usually text, the dates are always text, the categories you'll group by are text. In unit 14 you'll flatten a real World Bank response and find that the latitude, longitude, and population all arrive as text too.

So handling text well isn't a warm-up before the real work. It's roughly half of what data cleaning actually *is*.

---

## 2. Writing text down

You put text in quotes, and Python treats single and double quotes as identical. Pick one and stay consistent — this course uses double.

```python
a = "double"
b = 'single'
c = 'He said "hi"'
```

That third line shows the practical reason to have two: if your text contains a double quote, wrapping it in single quotes means you don't have to do anything special.

If you can't avoid it, you can **escape** a character — put a backslash in front of it to say "treat this as literal text, not as punctuation." So `"He said \"hi\""` works too. The escape sequences worth knowing are `\n` for a line break, `\t` for a tab, and `\\` for an actual backslash.

That last one is why Windows file paths cause trouble. Write `"C:\Users\name"` and Python sees `\U` and `\n` and tries to interpret them as escape codes, which produces either garbage or an error. The fix is a **raw string** — put an `r` before the opening quote and Python turns escape processing off entirely:

```python
path = r"C:\Users\rohan\data.json"
```

You'll want this whenever you type a Windows path into code, which on your machine is fairly often.

---

## 3. Text is a sequence, and it is frozen

Two properties do almost all the work in this lesson, so it's worth being precise about both.

**A string is a sequence.** That means it has a length, its characters have an order, and each one has a numbered position. Positions start at zero, not one — the first character is at position 0.

```python
s = "python"
len(s)      # 6
s[0]        # "p"
s[1]        # "y"
s[-1]       # "n"
```

That last one is a genuinely nice Python feature: negative positions count backwards from the end, so `s[-1]` is always the last character regardless of length. You never have to write `s[len(s) - 1]`.

You can also ask whether something appears inside:

```python
"tho" in s      # True
```

**A string is immutable** — meaning once it exists, it cannot be changed. Not "shouldn't be." Cannot.

```python
s[0] = "P"      # error: strings don't support this
```

This sounds like a limitation and mostly isn't, but it has one consequence that catches absolutely everybody exactly once. Every method that looks like it modifies a string — `.upper()`, `.strip()`, `.replace()` — actually **builds a brand new string and hands it back**, leaving the original completely untouched.

```python
name = "  Rohan  "
name.strip()
print(name)          # "  Rohan  " — nothing happened
```

The strip worked perfectly. It computed the string `"Rohan"` and then threw it away, because you didn't do anything with the result. What you needed was:

```python
name = name.strip()
```

That's the fix, and it's the same fix every time. **If a string method appears to have done nothing, you forgot to catch the result.** Remember it now and it'll save you a confused ten minutes later.

---

## 4. Slicing — taking a piece out

**What it is.** Slicing gives you a section of a string, written as `s[start:stop]`. The start position is included and the stop position is **not**.

```python
s = "abcdefg"
s[2:5]     # "cde"    — positions 2, 3 and 4
```

Either end can be left off, and Python fills in "the beginning" or "the end":

```python
s[:3]      # "abc"
s[3:]      # "defg"
s[-2:]     # "fg"      — last two characters
s[:-1]     # "abcdef"  — everything except the last
```

There's a third, optional part, the step, which says how many to move each time:

```python
s[::2]     # "aceg"    — every second character
s[::-1]    # "gfedcba" — backwards
```

**Why "stop is excluded" is the right design**, even though it feels arbitrary at first. Because it makes two things always true: the length of `s[a:b]` is exactly `b - a`, and `s[:n] + s[n:]` always reassembles the original with nothing lost or duplicated. Under the other convention you'd be adding and subtracting one constantly. It's worth internalising, because the identical rule applies to lists in unit 03.

**The practitioner's detail.** Slicing never fails. Ask for a position past the end and you get an error; ask for a *slice* past the end and you just get whatever was there, possibly nothing:

```python
"abc"[10]        # error
"abc"[10:20]     # ""      — no error at all
```

That's why truncating text with `text[:100]` is safe on a string of any length, including an empty one. When you're processing a thousand records of unknown content, that reliability matters.

---

## 5. The methods you'll actually reach for

A **method** is a function that belongs to a value and is called by putting a dot after it. You've already seen `.strip()`. There are dozens on strings; these are the ones that earn their place.

**Cleaning up whitespace and case.** `.strip()` removes spaces, tabs and line breaks from both ends of a string (`.lstrip()` and `.rstrip()` do one end only). `.lower()` and `.upper()` convert case, and `.title()` capitalizes each word.

```python
"  hi  ".strip()       # "hi"
"HELLO".lower()        # "hello"
```

The habit to build: **lowercase text before you compare it.** `"USA" == "usa"` is `False`, and that single fact is responsible for an enormous number of rows silently failing to match during a join. If you're comparing anything that came from a human or an API, `.lower()` both sides first.

**Splitting apart and joining together.** `.split()` breaks a string into a list of pieces:

```python
"a,b,c".split(",")        # ["a", "b", "c"]
"2024-01-05".split("-")   # ["2024", "01", "05"]
"a  b   c".split()        # ["a", "b", "c"]
```

That last one is worth a second look. Called with no argument at all, `.split()` splits on *any run of whitespace* and quietly discards empty results — which is exactly what you want for messy human-typed text. Called with a specific separator, it splits on each individual occurrence, so `"a,,b".split(",")` gives you `["a", "", "b"]` with an empty string in the middle. Both behaviours are correct; you just need to know which one you asked for.

Going the other way is `.join()`, and its shape reads backwards until it clicks: you call it **on the separator**, and hand it the pieces.

```python
",".join(["a", "b"])      # "a,b"
"".join(["a", "b"])       # "ab"
```

It only accepts text. `",".join([1, 2])` fails, because 1 is a number. Convert first: `",".join(str(n) for n in numbers)`.

**Asking questions.** `.startswith()` and `.endswith()` do what they say, and `.endswith()` accepts several options at once if you give it a group in parentheses. For "does this appear anywhere," just use `in`, which is cleaner than the alternatives.

```python
"data.json".endswith((".json", ".csv"))    # True
"son" in "data.json"                        # True
```

There's also `.isdigit()`, which reports whether a string is made entirely of digits. It's useful and it has a sharp edge: it says `False` for `"3.5"`, because a dot is not a digit, and `False` for `"-7"`, because a minus sign isn't either. It also says `False` for the empty string. Any one of those will bite you if you use it as a general "is this a number" test — which, in fact, is exactly what the task will ask you to think about.

**Replacing.** `.replace(old, new)` swaps every occurrence, or you can cap it: `.replace("-", "_", 1)` changes only the first.

**Trimming prefixes and suffixes.** `.removeprefix()` and `.removesuffix()` strip a known start or end, and — importantly — do nothing at all if it isn't there:

```python
"data.json".removesuffix(".json")      # "data"
"data.csv".removesuffix(".json")       # "data.csv" — unchanged, no error
```

That's much safer than slicing by a hardcoded length, because it can't silently chop the wrong number of characters off something that didn't match your assumption.

---

## 6. f-strings, properly

Unit 01 introduced these. Here's the full picture, because good output is worth more than people think.

The `f` before the quote means anything inside curly braces gets evaluated and inserted:

```python
name, n = "torvalds", 8

f"{name} has {n} repos"      # "torvalds has 8 repos"
f"{n * 2}"                    # "16"
f"{name.upper()}"             # "TORVALDS"
f"{'yes' if n else 'no'}"     # "yes"
```

Any expression works in there, not just a bare variable.

**Format codes** go after a colon and control how the value is rendered:

```python
f"{3.14159:.2f}"    # "3.14"        two decimal places
f"{1234567:,}"      # "1,234,567"   thousands separators
f"{0.4567:.1%}"     # "45.7%"       as a percentage
f"{8:>6}"           # "     8"      right-aligned in a 6-wide column
f"{8:<6}|"          # "8     |"     left-aligned
f"{8:06}"           # "000008"      zero-padded
```

Alignment is what turns dumped output into something that looks considered, and it costs one extra character:

```python
for key, value in stats.items():
    print(f"{key:>15}: {value}")
```

The convention that reads best is labels left-aligned, numbers right-aligned — because right-aligned numbers line their digits up, so you can compare magnitudes at a glance. Thirty seconds of this is genuinely the difference between "here are the numbers" and "here is the answer," and an interviewer reading your screen will register it.

Two more, both small and both useful. Putting `=` after an expression prints the expression *and* its value, which is the fastest debugging print in Python:

```python
f"{n=}"     # "n=8"
```

And `!r` shows the value the way Python would write it, with quotes and escape codes visible:

```python
s = "hi\n"
f"{s}"      # hi, then a line break
f"{s!r}"    # "'hi\\n'"
```

That's how you catch invisible problems. If two strings that look identical refuse to compare equal, `!r` will show you the trailing space or stray newline that's causing it. That single trick has saved more debugging hours than it has any right to.

---

## 7. Characters versus bytes — the one paragraph you need

A `str` is a sequence of **characters** — letters, digits, emoji, accented vowels. But networks and files don't move characters; they move raw **bytes**, which are just numbers from 0 to 255. The rule that maps between the two is called an **encoding**, and in 2025 the answer is essentially always UTF-8.

```python
"café".encode("utf-8")            # b'caf\xc3\xa9'   — characters to bytes
b'caf\xc3\xa9'.decode("utf-8")    # 'café'           — bytes back to characters
```

You need this for exactly two reasons in this course. First, when you fetch a URL you'll get both `r.content` (the raw bytes) and `r.text` (the decoded characters), and you'll want the second one. Second, and more practically: on Windows, opening a file without saying which encoding to use falls back to a legacy regional codepage that mangles anything outside plain English. Country names, city names, and people's names are full of accents. That's why every `open()` in this course passes `encoding="utf-8"` explicitly, and why yours should too. Get it right once and you'll never think about it again.

---

## 8. What I have deliberately left out

The task needs a couple of things I haven't shown you, plus a couple worth meeting anyway. Go and find them — the interactive prompt (`python`, then `help(str.rsplit)`) is the fastest route.

- `str.rsplit()` — how it differs from `.split()`, and when that difference matters.
- `str.partition()` — splits into exactly three parts, always, which makes it predictable in a way `.split()` isn't.
- `str.count()` — how many times something appears.
- `str.casefold()` — a stricter version of `.lower()`, and why non-English text needs it.
- What `"a,b,,c".split(",")` returns, and why there's an empty string in the result.

---

## 9. Check yourself

1. `s = "hello"`, then `s.upper()`, then `print(s)`. What prints, and why?
2. What does `"abcdef"[1:-1]` give?
3. Why does `",".join([1, 2])` fail?
4. How would you display `0.8231` as `82.3%`?
5. What's the difference between `"a b  c".split()` and `"a b  c".split(" ")`?
6. Why does every file in this course get opened with `encoding="utf-8"`?

*(Answers: 1. `hello` — `.upper()` returned a new string and you didn't keep it. 2. `"bcde"`. 3. `.join` requires every piece to be text, and `1` is a number. 4. `f"{0.8231:.1%}"`. 5. the first splits on runs of whitespace giving `["a","b","c"]`; the second splits on each single space giving `["a","b","","c"]` with an empty string where the double space was. 6. because Windows otherwise defaults to a legacy codepage that corrupts accented characters.)*

---

*Three things to carry forward. Strings are immutable, so every method returns a new one and you have to catch it — that's the same "names point at objects" idea from unit 01, seen from the other side. Slicing uses a half-open range and never raises, which makes it the safe way to take a piece of anything. And lowercasing before comparing is a habit, not a special case, because mismatched case is the quietest way for real records to fail to match. Unit 03 reuses the slicing rules on lists, so what you just learned about `[2:5]` will already be familiar there.*

*Now open [`task.py`](task.py).*
