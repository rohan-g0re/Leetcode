# 08 — Errors and Exceptions

*This lesson takes about twenty-five minutes and it settles two debts the course has been carrying. In unit 01 you wrote `coerce_number` the hard way — inspecting the type of a value by hand before daring to convert it — because the proper tool didn't exist yet. In unit 04 you used the `or {}` trick to stop a null licence field from blowing up a lookup chain. Both of those were you working to* prevent *an error. This unit teaches the other half of the craft: let the error happen, and catch it. Nothing here assumes anything past unit 07.*

*One piece of housekeeping first. `SETUP.md` section 0.6 already teaches you how to read a traceback — bottom line first, then work upward through the call chain. If you haven't read it, go and read it now; three minutes there will save you an hour later. This lesson assumes you can look at an error and find the type and the message in it.*

---

## 1. Why this unit exists at all

Every lesson in Part 1 has been circling the same fact: **real API data is untrustworthy.** Fields go missing. A field that held a number last week holds the string `"42"` this week. A field documented as always present arrives as `null` for the one record you happen to be looking at. And that's before the network gets involved — servers time out, connections get refused, and an endpoint that promised you JSON hands back an HTML error page instead.

You have two options when you touch data like that. You can check everything before you touch it, which is what you've done so far. Or you can attempt the operation and have a plan ready for when it fails. The second approach is what this unit is about, and in Python it's usually the better one: shorter, more readable, and it handles failure cases you didn't think to check for. The concrete payoff — unit 01's `coerce_number` took a dozen fiddly lines and still choked on scientific notation like `"1e3"`. The version you'll write today is two lines and handles everything.

---

## 2. What an exception actually is

You have already seen plenty of errors, and the natural way to read them is "my program broke." That's not what happened. Something much more specific and much more controllable happened, and once you see the mechanism you can start steering it.

When an operation goes wrong, Python builds an **exception** — an actual object, sitting in memory, carrying two useful things: a *type* saying what kind of failure this is, and a *message* saying what specifically went wrong. Then Python **raises** it. "Raise" is the word for throwing this object into the air and abandoning whatever it was doing.

```python
int("abc")
# ValueError: invalid literal for int() with base 10: 'abc'
```

`ValueError` is the type. Everything after the colon is the message. Both matter, and they matter differently: **you catch by type, and you read the message.** You'll never write code that inspects the message text — that's for humans. The type is what your code makes decisions on.

Now the part that matters most. While your program runs, Python keeps track of which function called which — `main` called `process`, which called `parse`, which called `int`. That chain of unfinished calls is the **call stack**. When `int` raises its `ValueError`, Python abandons `int` and hands the exception to `parse`. If `parse` has no plan for it, Python abandons `parse` too and hands it to `process`, and so on upward, one caller at a time. That upward journey is called **propagating**, and a piece of code that stops it is a **handler**.

If nobody handles it, the exception falls out of the top of your program, the program stops, and Python prints the **traceback** — the record of every level it passed through. That's why a traceback is a *list* of frames rather than one line: it's the exception's travel history, printed oldest call first.

So the mental model to carry out of this section: **a raised exception is a flare fired up the ladder of unfinished function calls. The first handler that recognizes its type grabs it. If no one does, it exits the top of the building and you get a traceback.** Every technique in the rest of this lesson is about deciding where on that ladder you want to stand, and which flares you're willing to catch.

One practitioner's detail while you're here. When you turn an exception into text with `str()`, you get the message alone — no type name. And `KeyError` is odd: its message is the *repr* of the missing key, so `str()` of a `KeyError` for the key `x` gives you `'x'` with the quote marks included. That's not a typo; it will show up in this unit's task, and it surprises people the first time.

---

## 3. `try` and `except`

The handler is a `try`/`except` block, and it looks like this:

```python
try:
    value = int(text)
except ValueError:
    value = None
```

Read it as: attempt the indented code under `try`; if a `ValueError` comes flying out of it, stop there and run the code under `except` instead. If nothing goes wrong, the `except` block is skipped entirely as though it weren't there.

The single most important thing about this shape is that **only the code inside `try` is protected**. The mental model: `try` is a fenced-off area, not a mood — it doesn't make the surrounding function careful, it protects exactly the lines you put inside it. So keep it small. Wrap thirty lines in a `try` and let one of them contain a typo, and your handler will catch the typo's error, swallow it, and leave you wondering all afternoon why a list came out empty. One or two risky lines inside the fence, everything else outside.

**Catching several types at once.** Often two different failures mean the same thing to you. `float("abc")` raises `ValueError` because the text isn't a number. `float(None)` raises `TypeError` because `None` isn't the kind of thing you can convert at all. As far as your program is concerned both mean "that wasn't a number," so one handler covers both:

```python
try:
    value = float(raw)
except (ValueError, TypeError):
    value = None
```

The parentheses are required — that's a tuple of types, exactly like unit 03's tuples. And that four-line block is the whole of unit 01's `coerce_number`, done properly. Sit with that comparison for a moment, because it's the clearest argument for this style you'll get.

**Getting hold of the exception object.** Sometimes you want the thing itself, not just to know it happened. Add `as` and a name:

```python
try:
    risky()
except ValueError as exc:
    print(f"bad value: {exc}")
```

`exc` is now the exception object. `str(exc)` is its message, and `type(exc).__name__` is the name of its type as a string — `"ValueError"`. Those two together let you build a readable one-line description of any failure, which is exactly what the task's `describe_exception` asks for.

**`else` and `finally`.** Two optional extras:

```python
try:
    data = fetch()
except TimeoutError:
    data = None
else:
    print("worked")
finally:
    cleanup()
```

The `else` block runs only when *no* exception was raised, and it exists to keep your fence tight: risky call in `try`, follow-up work in `else`, so the follow-up's own bugs aren't caught by your handler. The `finally` block runs *always* — whether things went well, went badly, or the exception is still travelling up the ladder. It's for cleanup that must happen either way, like closing a file, though you'll meet a nicer tool for that (`with`) in unit 09.

---

## 4. `except: pass`, and why reviewers hate it

This is the most criticized pattern in Python, and it's worth knowing precisely why, because "it's bad practice" is not an answer that survives a follow-up question.

```python
try:
    do_everything()
except:
    pass
```

There are two separate crimes here and they're independent of each other.

The first is the **bare `except:`** with no type after it. That catches *everything* — including `KeyboardInterrupt`, the exception Python raises when you press Ctrl+C, and `SystemExit`, the one raised when something asks the program to quit. Put a bare except inside a loop and you have built a program you cannot stop from the keyboard. If you genuinely need to catch broadly, write `except Exception:` instead. `Exception` covers every error your code can meaningfully recover from and deliberately excludes those two.

The second crime is the **`pass`**, which is Python's word for "do nothing." It destroys the information. A real bug — a typo in a key name, a function returning the wrong shape — gets caught, discarded without trace, and reappears an hour later as an empty list you cannot explain. The mental model: **`except: pass` is a smoke alarm with the battery taken out.** The building can still burn; you've just arranged not to hear about it.

So what do you do when you genuinely *do* want to keep going past a failure? You continue, and you **count**:

```python
failures = []
good = []
for record in records:
    try:
        good.append(transform(record))
    except (KeyError, ValueError) as exc:
        failures.append({"id": record.get("id"), "error": str(exc)})

print(f"processed {len(good)}, skipped {len(failures)}")
```

That last line is the whole point. You didn't crash, you didn't pretend everything was fine, and you can say exactly how much of your input survived. This `(good, failures)` shape — returning both lists rather than printing the failures — is the practitioner's version, because it lets the caller decide whether to warn, abort, or ignore. You'll build exactly this in the task's `parse_records`.

And it's worth saying out loud in the interview. *"I processed 487 of 500 records; the 13 that failed were missing an amount field, and here they are."* That sentence costs you nothing and reads as someone who has handled real data rather than examples.

---

## 5. Catching narrowly, and the one time you shouldn't

The rule is short: **catch the specific exception you actually have a plan for, and let everything else crash.**

```python
except Exception:     # too broad — hides typos and logic errors
except KeyError:      # precise — "I know this field is sometimes absent"
```

The narrow version is a statement of knowledge: you anticipated this exact failure, and here is your response to it. Anything you *didn't* anticipate should propagate all the way up and stop the program loudly, because that's a bug, and a bug you find in thirty seconds is worth ten of the kind you find in an hour.

There is one legitimate exception, and it comes up in real work. Imagine a batch job walking fifty thousand records over two hours. Record 31,204 is malformed in a way nobody predicted. Under the strict rule your run dies at the ninety-minute mark and you get nothing. So around *each item* — not around the whole job — a broad `except Exception` with logging is the right call, because the cost of losing the run exceeds the cost of a vague error report. What makes it acceptable is the discipline from the previous section: log every one, report the count.

The same reasoning justifies the task's `first_successful`, where you try a list of sources in order — cache, then API, then default — and move to the next one whenever anything at all goes wrong. There, broad is correct: you truly don't care *why* a source failed, only that it did.

---

## 6. EAFP and LBYL

These two acronyms name the choice this whole lesson is about, and knowing the names is genuinely useful because it lets you *justify* your style instead of just having one.

**LBYL** is "Look Before You Leap" — check first, then act. It's what you did in units 01 and 04.

```python
if "score" in record and record["score"] is not None:
    value = float(record["score"])
```

**EAFP** is "Easier to Ask Forgiveness than Permission" — act, and handle the failure.

```python
try:
    value = float(record["score"])
except (KeyError, TypeError, ValueError):
    value = None
```

Python culture leans EAFP, for three reasons worth having ready. It's faster when failures are rare, because the successful path pays no cost for a check that almost always passes. It catches failure modes you didn't enumerate — notice the LBYL version above still crashes if `score` holds the string `"n/a"`. And there's a subtler one that matters with files: between your check and your action, the world can change. A file that existed when you asked can be deleted before you open it. That gap is called a race condition, and EAFP has no gap.

Use LBYL when the check is trivially cheap and clearer to read — `.get()` on a dictionary is LBYL and it's still the right tool most of the time. The task's `safe_field` asks you to rewrite unit 04's `deep_get` in the EAFP style, so you'll have written the same function both ways and can speak to the difference.

---

## 7. Raising errors of your own

You can fire a flare too, with `raise`:

```python
if page_size > 100:
    raise ValueError(f"page_size must be <= 100, got {page_size}")
```

The principle is **fail at the door, not in the basement.** Validate a function's inputs at the top and reject bad ones immediately, because an error at the point of the bad value is trivial to diagnose, while the same value surfacing two hundred lines later as a confusing symptom is not. Notice the message includes the offending value — not decoration, but the difference between a traceback that tells the reader what to fix and one that makes them go looking. The task checks for exactly this.

Pick a built-in type that fits: `ValueError` for the right type with a wrong value, `TypeError` for the wrong type entirely, `KeyError` for a missing key, `NotImplementedError` for a stub you haven't written yet.

**When you want your own type**, it's one line:

```python
class ValidationError(Exception):
    """Raised when input data fails a check we care about."""
```

That's a **subclass** of `Exception`, which is unit 10's material, but the idea you need right now is simple: `ValidationError` is a more specific kind of `Exception`, so it inherits everything `Exception` can do, and — this is the load-bearing part — anyone catching `Exception` will also catch your `ValidationError`, while anyone catching `ValidationError` specifically will *only* get yours. You define one when callers need to tell *your* failures apart from Python's. FastAPI's `HTTPException`, which you'll meet in unit 23, is exactly this pattern.

**Re-raising** is for when you want to observe an error without swallowing it:

```python
try:
    risky()
except ValueError:
    log_it()
    raise
```

A bare `raise` inside an `except` block throws the *same* exception onward, with its original traceback intact — so the flare resumes its journey up the ladder from where it was caught. That's different from writing `raise ValueError(...)` again, which would start a fresh traceback and lose where the trouble actually began.

And when you want to wrap a low-level failure in your own vocabulary:

```python
raise ValidationError("could not parse response") from exc
```

`from exc` chains the two, so the printed traceback shows both the original cause and your wrapper. It's a small touch and it makes debugging your own libraries much less painful.

---

## 8. The exceptions you'll actually meet

Here is the working set. You needn't memorize it, but recognize every row on sight — the type is what tells you where to look.

| Exception | Typical cause in this course |
|-----------|------------------------------|
| `KeyError` | dict missing a key — the API omitted a field |
| `IndexError` | list too short — you assumed there was a result |
| `TypeError` | `None` where a value was expected; wrong argument type |
| `ValueError` | `int("abc")`; a bad argument to a function |
| `AttributeError` | you called a method on `None` |
| `ZeroDivisionError` | the average of an empty group |
| `FileNotFoundError` | wrong path |
| `json.JSONDecodeError` | the response wasn't JSON — often an HTML error page |
| `requests.Timeout` | the server didn't answer in time |
| `requests.HTTPError` | raised by `raise_for_status()` on a 4xx or 5xx |
| `requests.ConnectionError` | DNS failure, refused connection, no network |

Two things in that table deserve real attention, and both hinge on the idea of a **hierarchy** — exception types are arranged in a family tree, where catching a parent type also catches every one of its descendants.

`json.JSONDecodeError` is a child of `ValueError`. In plain words: it *is* a `ValueError`, just a more specific flavour of one, so `except ValueError:` catches it without you naming it. That's why a malformed JSON response can be handled by the same handler you already wrote for bad numbers — occasionally convenient, occasionally a nasty surprise when your number-parsing handler quietly swallows a broken API response. Know which you're doing.

The bottom three rows are all children of `requests.RequestException`, which means **one line catches every network-layer failure there is**:

```python
except requests.RequestException:
```

That is the single most valuable line in this table. Memorize it. From unit 12 onward, every live call you make gets wrapped in it, because you cannot enumerate all the ways a network fails and you don't need to.

The practitioner's detail here, and it catches almost everyone: **`requests` does not raise an exception when the server returns a 404 or a 500.** As far as the library is concerned it asked for a page and got an answer; the answer just happened to be an error. You have to ask for that behaviour explicitly by calling `response.raise_for_status()`, which is what turns a bad status code into `requests.HTTPError`. Skip that line and your code will cheerfully try to parse an error page as if it were data. Unit 12 will hammer this in properly.

While we're on family trees, one that will bite you in this unit's task: **`bool` is a subclass of `int`.** `True` really is a kind of integer — which follows straight from unit 01, where you learned that `True` behaves as `1`. The consequence is that `isinstance(True, int)` is `True`, so a type check written the obvious way will let booleans through where you meant to allow only whole numbers. The task's `validate_page_size` requires you to reject `True`, and this is why it's harder than it looks.

---

## 9. What I have deliberately left out

Five things below are deliberately missing, and finding them yourself is the point — reading documentation under mild time pressure is the most transferable skill in this course, and the one thing a tutorial that hands you everything can never teach. The interactive prompt (`python` on its own, then `help(...)`) is the fastest way through all of them.

Look up `contextlib.suppress(KeyError)`, a tidy one-line way to ignore one specific exception when you genuinely have nothing to do about it. Look at the exception hierarchy itself and satisfy yourself why `except Exception:` misses `KeyboardInterrupt` — the answer is in the shape of the tree. Find out what `warnings.warn()` does and when you'd reach for it instead of raising. Skim the `logging` module, especially `logging.exception()`, which records a failure with its full traceback rather than just its message. And read about `assert` — specifically why Python deletes every assert statement under the `-O` flag, which is why you must never use one to validate user input.

---

## 10. Check yourself

Answer these before opening the task. If one isn't obvious, rereading the section is cheaper than getting stuck later without knowing why.

1. Why is `except: pass` considered harmful — two separate reasons?
2. Which exception does `int("abc")` raise? What about `int(None)`?
3. When does `finally` run? When does `else` run?
4. What does a bare `raise` inside an `except` block do?
5. What's the one-line way to catch every `requests` network failure?
6. Why keep the `try` block small?
7. Why does `isinstance(True, int)` return `True`?

*(Answers: 1. the bare `except` catches `KeyboardInterrupt` and `SystemExit` too, so the program becomes unkillable, and the `pass` destroys the information so a real bug disappears silently. 2. `ValueError` — the text isn't a number; `TypeError` — `None` isn't a convertible kind of thing at all. 3. `finally` always, whatever happened; `else` only when no exception was raised. 4. it re-raises the same exception object with its original traceback intact, so it resumes travelling up the call stack. 5. `except requests.RequestException:`, because every network failure type is a child of it. 6. because any unrelated bug inside the fence gets caught and swallowed by your handler. 7. because `bool` is a subclass of `int` — `True` genuinely is a kind of integer.)*

---

*Three things to carry out of this unit. First, an exception is an object with a type and a message that travels up the chain of unfinished calls until something catches it — so "my program broke" is really "nobody on the ladder had a plan for this," and your job is to decide where to stand and what to catch. Second, the honest way to survive bad data is to catch narrowly, collect the failures, and report the count; `except: pass` fails both halves of that. Third, `except requests.RequestException:` is the line that will wrap every live call you make from unit 12 onward, and `raise_for_status()` is the line that makes it fire. This is also the unit where unit 01's `coerce_number` finally becomes two lines and unit 04's `deep_get` becomes a `try` block — you're not learning a new topic so much as being handed the tool the earlier ones were missing.*

*Now open [`task.py`](task.py).*
