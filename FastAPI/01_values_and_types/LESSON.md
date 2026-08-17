# 01 — Values, Types, and Variables

*This is the first lesson of the course and it assumes you have never written a line of Python. Read it straight through — about fifteen minutes — then open `task.py`. Every word you need is defined here, at the moment it first appears. Nothing is treated as "you probably already know this." If you hit a term that wasn't explained, that's a mistake in this document, not a gap in you.*

*One thing before we start: you already know SQL. That's genuinely useful here, and I'll point at the connection whenever it helps, because the mental models transfer better than you'd expect.*

---

## 1. What you are actually learning to read

Everything in this first part of the course is aimed at one moment: an interviewer sends you a web address, you fetch it, and text comes back that looks like this.

```
{"login": "torvalds", "public_repos": 8, "followers": 200000,
 "name": null, "site_admin": false, "score": 24.5}
```

That blob is called **JSON** — it's just a text format for writing down structured data, and it's what almost every web service on earth replies with. Your job, over and over, will be to turn that text into something Python can work with and then pull answers out of it.

Look closely at what's actually *in* there. There's a piece of text (`"torvalds"`). There are whole numbers (`8`, `200000`). There's a number with a decimal point (`24.5`). There's a true-or-false value (`false`). And there's something called `null`, which means "this field exists but there's nothing in it."

That's five kinds of thing, and that is the *entire* vocabulary. Every JSON response you ever meet is built from those five pieces plus two ways of grouping them together (which are units 03 and 04). So this lesson is not abstract warm-up — it is you learning to recognize the five raw materials you'll be handling every single day of this course.

---

## 2. Types, and why Python insists on knowing

**What it is.** Every single value in Python has a **type** — a label saying what kind of thing it is. The number `5` has the type `int` (short for integer). The text `"5"` has the type `str` (short for string, which is programmer-speak for "some text"). They look similar on the page and they behave completely differently.

You can always ask Python what type something is, using a built-in tool called `type`:

```python
type(5)        # int
type(5.0)      # float
type("5")      # str
type(True)     # bool
type(None)     # NoneType
```

**Why it matters.** The type decides what operations *mean*. Watch:

```python
5 + 5        # 10
"5" + "5"    # "55"
```

Same `+` symbol, wildly different result. With two numbers, `+` adds. With two pieces of text, `+` glues them end to end. Python didn't ask you which one you wanted — it looked at the types and decided.

This is the mental model to carry out of this section: **the type is what tells Python how to behave, so "what type is this?" is the first question to ask about any value you didn't create yourself.** And every field of every API response is a value you didn't create yourself.

**Where this bites you.** Real services are inconsistent about this in a way that will genuinely cost you time. One API returns `{"population": 1400000}` — a number. Another returns `{"population": "1400000"}` — the same information as *text*. If you don't notice, and you try to add up a column of those, Python will happily glue the strings together into one enormous nonsense string and never raise a single complaint. You'll be looking at a wrong answer that looks plausible. In unit 14 you'll meet a real dataset from the World Bank where the latitude and longitude arrive as text, exactly like this. When it happens, you'll know why.

---

## 3. Whole numbers and decimal numbers

Python has two number types and the difference matters more than you'd guess.

`int` is a whole number: `8`, `-3`, `200000`. Python integers have no size limit — you can compute `2 ** 200` (that's 2 to the power of 200) and get an exact answer, which most languages can't do.

`float` is a number with a decimal point: `24.5`, `-0.001`, `3.0`. The name comes from "floating point," which is the technique computers use to store decimals in binary.

And that technique has one famous consequence you should meet now rather than in the middle of a task:

```python
0.1 + 0.2          # 0.30000000000000004
0.1 + 0.2 == 0.3   # False
```

That is not a Python bug. Computers store numbers in binary — powers of two — and one-tenth simply cannot be written exactly in binary, the same way one-third can't be written exactly in decimal (0.3333... never ends). So `0.1` is stored as something microscopically off, and the error shows up when you add.

Two working rules come out of this. **Never compare two floats with `==`**; instead check whether the difference between them is tiny. And **never use floats for money** — use whole numbers of cents, so £1.99 is stored as the integer `199`.

Mixing the two types is fine and Python handles it for you: `3 + 0.5` gives `3.5`. Any float anywhere in the sum makes the whole answer a float.

---

## 4. Text, true-or-false, and nothing-at-all

**Text (`str`)** goes in quotes, and Python doesn't care whether you use single or double as long as you're consistent: `"hello"` and `'hello'` are identical. Unit 02 is entirely about text, so I'll leave it there.

**True and false (`bool`)** is the type with exactly two possible values, `True` and `False`. Note the capital letters — writing `true` gets you an error, because Python has never heard of it.

Here's a quirk worth knowing early, because it turns into a genuinely useful trick. Underneath, Python treats `True` as `1` and `False` as `0`. Which means you can *add up* a column of true/false values to count how many are true:

```python
flags = [True, True, False, True]
sum(flags)      # 3
```

Later in the course you'll want to answer "how many of these records have an ID?" and this is how you'll do it in one line.

**Nothing-at-all (`None`)** is the strangest of the five and the most important for our purposes. `None` is a single special value meaning "there is no value here." It is **not** zero, it is **not** empty text, and it is **not** `False`. It's the absence of a value rather than any particular value.

You will meet `None` constantly, because it's what JSON's `null` becomes when Python reads it. Look back at that GitHub response at the top — `"name": null`. That user has no display name set. When Python parses that response, the name field will be `None`.

There is exactly one `None` in a running Python program — every `None` is literally the same object in memory. Because of that, the correct way to test for it is with the word `is`:

```python
if x is None:
    ...
if x is not None:
    ...
```

`is` asks "are these the exact same object?" while `==` asks "do these have equal value?" For `None`, identity is the right question, it's faster, and — the practitioner's reason — it can't be fooled. Python lets a class define its own meaning for `==`, so a sufficiently strange object could claim to be equal to `None` when it isn't. Nothing can fake being the same object. This is why every Python style guide insists on `is None`, and why reviewers notice when you write `== None`.

---

## 5. Variables are names, not boxes

**What it is.** When you write this:

```python
x = 5
```

the almost-universal way people first picture it is: there's a box called `x`, and the number 5 goes inside it. That picture is wrong, and it will eventually produce a bug you cannot explain.

Here's the true picture. The value `5` is an object living somewhere in memory. The `=` doesn't put it anywhere — it **binds the name** `x` to that object. A variable is a *label* pointing at a thing, not a container holding a thing.

**Why this is worth the effort of relearning.** Because a value can have more than one label on it:

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)          # [1, 2, 3, 4]
```

Read that again. We changed `b`, and `a` changed too. Under the box picture that's madness. Under the label picture it's obvious — `b = a` didn't copy anything; it stuck a second label on the one list that already existed. There is only one list here. `a` and `b` are two names for it.

**Where it shows up.** This only causes trouble for types that can be *changed in place*. Those are called **mutable** types, and the ones you'll meet are lists, dictionaries, and sets (units 03 and 04). The others — numbers, text, `True`/`False`, `None` — are **immutable**: you literally cannot alter them, so two labels on the same number can never surprise you.

That's the whole rule, and it's the thread that runs through the next three units. When you find yourself in unit 04 wondering why editing one record seems to have edited another one, come back to this paragraph. It'll be this.

Two smaller notes on names. Python doesn't require you to declare a type — `x` can hold a number now and text later, though rebinding a name to a different kind of thing usually means your code is confused, so don't. And the naming convention everyone follows is `snake_case` — lowercase words joined by underscores, like `total_stars` or `fetch_user`. Interviewers do notice. There's also one trap: avoid naming a variable `list`, `dict`, `type`, `sum`, `max`, or `id`, because those are the names of built-in tools, and shadowing one quietly breaks it for the rest of your program.

---

## 6. Doing arithmetic

Most of this is what you'd guess, but three of them aren't.

```python
7 + 2    # 9
7 - 2    # 5
7 * 2    # 14
7 / 2    # 3.5
7 // 2   # 3
7 % 2    # 1
7 ** 2   # 49
```

The three worth pausing on. `/` **always** produces a float, even when it divides evenly — `4 / 2` is `2.0`, not `2`. `//` is called floor division: it divides and then rounds *down* to a whole number. And `%`, called modulo, gives you the remainder.

That last pair sounds academic and isn't. `//` is how you sort values into buckets — `age // 10` turns 37 into 3, giving you the decade someone is in, which is exactly how you build an age histogram. And `%` is how you test divisibility: `n % 2 == 0` means "n is even," and `i % 100 == 0` fires on every hundredth iteration of a loop, which is the standard way to print progress without printing ten thousand lines.

One thing will genuinely break your program if you don't defend against it: **dividing by zero raises an error and stops everything.** This sounds like an edge case until you realise that computing an average is `total / count`, and `count` is zero the moment a category turns out to be empty. That guard —

```python
if count == 0:
    return None
return total / count
```

— is probably the single most common defensive line you'll write in this entire course. You'll write it in the task at the end of this lesson.

Finally, to change a variable in place, Python has shorthand: `count += 1` means `count = count + 1`. The same works for `-=`, `*=`, and the rest. Python does **not** have `++`, so don't reach for it.

---

## 7. Comparing, and combining comparisons

Comparison works how you'd expect — `==` for equal, `!=` for not equal, plus `<`, `>`, `<=`, `>=` — and every one of them produces `True` or `False`. Note that equality is a *double* equals; a single `=` means assignment, and mixing them up is the first typo everyone makes.

One nicety Python has that most languages don't: you can chain comparisons the way you'd write them in maths.

```python
if 0 < x < 100:
```

That reads exactly as it looks and is the normal way to write a range check.

To combine conditions, Python uses actual English words rather than symbols: `and`, `or`, `not`. So `if a and b`, not `if a && b`.

And they have a property that becomes a genuinely useful safety technique. They **short-circuit** — meaning Python evaluates them left to right and stops as soon as the answer is settled. In `a and b`, if `a` turns out to be false, the whole thing is false regardless, so Python never even looks at `b`.

That lets you write a guard and the thing it guards in a single line:

```python
if data and data[0]["id"]:
```

If `data` is empty, Python stops right there and never tries to reach into it. Written the other way round, that same line would crash. You'll use this shape constantly once you're handling responses that might come back with zero results.

---

## 8. Truthiness — the most useful trap in the language

**What it is.** Python lets you use *any* value where a true-or-false is expected, and it has rules for which values count as false. These are the false-ish ones, called **falsy**:

```
False    None    0    0.0    ""    []    {}
```

That's: false itself, nothing-at-all, zero, zero-point-zero, empty text, an empty list, and an empty dictionary. **Everything else in Python is truthy.**

**Why it exists.** It makes the common checks read like English. Instead of writing "if the length of items is greater than zero," you just write:

```python
if items:
```

which means "if there's anything in items." That's the idiomatic Python way and you should adopt it.

**Where it bites you, and this is the practitioner's detail of this whole lesson.** Notice that `0` is falsy. Now suppose an API hands you `{"count": 0}` — a field that is present, and valid, and whose correct value happens to be zero. If you write:

```python
if data["count"]:
```

that is `False`, and your code will treat a perfectly good record as if the field were missing. The bug won't show up in your testing, because your test data has non-zero counts. It shows up in production, on the one record where somebody genuinely had zero of something.

So learn the distinction now and keep it forever. When you mean **"is there anything here?"** use truthiness: `if items:`. When you mean **"is this field present and filled in?"** use `is not None`: `if value is not None:`. They are different questions and conflating them is one of the most common sources of quiet, wrong answers in data code.

---

## 9. Turning one type into another

Since API data arrives in whatever type the service felt like sending, you'll spend real time converting. The tools are named after the types:

```python
int("42")        # 42
float("3.14")    # 3.14
str(42)          # "42"
```

Two of them behave in ways that surprise people. `int(3.9)` gives `3`, not `4` — converting to an integer **truncates**, it chops the decimal off rather than rounding. If you want rounding, that's a separate tool: `round(3.567, 2)` gives `3.57`, where the second argument says how many decimal places to keep.

And `round` itself has a wrinkle worth knowing about before it confuses you: it uses **banker's rounding**, where a value sitting exactly halfway goes to the nearest *even* number. So `round(0.5)` is `0` and `round(1.5)` is `2`. It looks broken and isn't — it's deliberate, because always rounding halves upward introduces a slow upward bias across a large dataset. It's occasionally the reason a total is off by one.

The important part for this course is what happens when conversion *fails*. `int("abc")` doesn't return anything sensible — it raises an error and stops your program. So does `int(None)`, which is the case that will actually get you, because `None` is what a missing JSON field becomes.

For now, the way to handle that is to check the type *before* converting rather than converting and hoping. There's a much better tool for this — catching the error instead of preventing it — but it's unit 08, and part of the point of your first task is that you do it the hard way once so you understand what unit 08 is saving you from.

---

## 10. Printing things out, and leaving notes

You will want to see values while you work, and the way you do that is `print()`. But printing a bare value is rarely enough; you want a label with it. That's what **f-strings** are for:

```python
name = "torvalds"
repos = 8
print(f"{name} has {repos} repos")     # torvalds has 8 repos
```

The `f` before the opening quote means "format." Inside the quotes, anything you put in curly braces gets evaluated and its result dropped into the text. You can put whole expressions in there, not just variable names — `f"{repos * 2}"` works fine.

You can also control how a value is displayed, by adding a colon and a format code inside the braces. The one you'll use constantly is decimal places:

```python
f"{3.14159:.2f}"     # "3.14"
```

Unit 02 covers the rest of these properly. For now, `.2f` is enough to make your output look deliberate rather than dumped.

Two last small things. A `#` starts a **comment** — everything after it on that line is ignored by Python and exists purely for whoever reads the code next. And a string sitting immediately under a `def` line is a **docstring**, which is a comment that Python actually keeps and can show you later:

```python
def average(values):
    """Return the mean of the values, or None when there are none."""
```

Write one for every function you define in an interview. It costs five seconds and reads as professional.

---

## 11. What I have deliberately not told you

The task needs a few tools I've left out on purpose. Reading documentation under mild time pressure is the single most transferable skill in this whole course, and it's the one thing a tutorial that hands you everything can never teach. So: find these yourself, in the interactive Python prompt or at docs.python.org.

- `abs()` — what it does to a negative number.
- `min()` and `max()` — what happens when you give them two or more arguments.
- `isinstance(x, int)` — the proper way to ask "is this value an integer?", and why it's preferred over comparing types directly.
- What `int(True)` gives you, and why that follows from section 4.
- `math.isclose()` — the correct way to compare two floats, given section 3.

The fastest way to explore any of these is the interactive prompt. Type `python` on its own in the terminal, and then poke:

```python
>>> help(abs)
>>> dir("hello")
>>> type(True)
```

`help` prints the documentation for anything. `dir` lists everything you can do to a value. Two minutes there beats twenty minutes of guessing, and doing it in front of an interviewer reads as competence, not ignorance.

---

## 12. Check yourself

Answer these before you open the task. If one of them isn't obvious, the section that covers it is worth rereading — that's cheaper than getting stuck in the task and not knowing why.

1. What does `7 // 2` give, and what does `7 % 2` give?
2. Why is `0.1 + 0.2 == 0.3` false?
3. What's the difference in *meaning* between `x is None` and `x == None`?
4. After `a = [1]; b = a; b.append(2)`, what is `a`, and why?
5. Which of these are falsy: `0`, `"0"`, `[]`, `[0]`, `None`, `" "`?
6. Why is `if data["count"]:` a risky way to check whether a count field is present?

*(Answers: 1. `3` and `1`. 2. binary floating point can't represent 0.1 or 0.2 exactly, so the sum lands microscopically off. 3. `is` asks whether it's the one and only None object; `==` asks about equal value and can be redefined by a class. 4. `[1, 2]` — `b = a` bound a second name to one list rather than copying it. 5. falsy: `0`, `[]`, `None`; truthy: `"0"`, `[0]`, `" "` — a string with a space in it is not empty. 6. because `0` is falsy, so a present, valid, zero value looks exactly like a missing one.)*

---

*The three ideas actually worth carrying out of this lesson: every value has a type and the type decides what operations mean, so the first question about any unfamiliar data is "what type is this"; a variable is a name pointing at an object rather than a box holding one, which is why changing something through one name can change it through another; and `None` is Python's word for "this field was empty," which means it's what most of a real API response's missing pieces will turn into. Those three threads run through the whole of Part 1 — the type question becomes unit 03's choice of container, the naming question becomes unit 04's copying bugs, and `None` becomes the reason unit 04 spends so long on how to read a field that might not be there.*

*Now open [`task.py`](task.py).*
