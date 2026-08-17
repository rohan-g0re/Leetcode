# Unit 01 — hints

*Open this only after about ten minutes of genuine effort on a function — not before. The struggle is where the learning happens, and a hint read too early takes that away from you. Read the section for the one function you're stuck on and then close the file again.*

---

### `describe_type`

Start in the interactive prompt rather than in the file. Type `python` on its own in the terminal, then try `type(5)`. You'll see `<class 'int'>` come back. That's a type object being displayed, and the name you want — `int` — is buried inside that display, not sitting there as clean text you can return.

So the question is how to get the bare name out. Run this:

```python
dir(type(5))
```

`dir` lists every attribute attached to a value. Scan the list for one that sounds like it holds a name; it will be surrounded by double underscores on both sides, which is Python's convention for "internal machinery". Once you've spotted it, try reading it off directly and see what you get back.

The reason this works is that Python types genuinely carry their own name as a piece of text, so you're not converting or parsing anything — you're just reading a label that was already there. The only step left is that the examples all want lowercase, and strings have a method for that.

---

### `safe_divide`

This one is two lines of logic and no cleverness. One `if` that catches the zero denominator and returns None, and then the plain division underneath it.

```python
if denominator == 0:
    return None
return numerator / denominator
```

The shape matters more than the content. Notice that the guard comes *first* and returns immediately, so by the time you reach the division you already know it's safe. That pattern — check the dangerous case up front, bail out, then do the real work on the last line without any nesting — is called an early return, and you'll write it constantly. It keeps functions flat and readable instead of burying the real work inside an `else`.

One thing to be aware of: `/` always gives back a float, so `safe_divide(0, 5)` produces `0.0` rather than `0`, which is exactly what the examples ask for. You don't need to do anything to make that happen.

---

### `is_missing`

The order of your checks is the entire difficulty here. Ask about None first, before you touch the value in any other way:

```python
if value is None:
    return True
```

That has to come first because the next step calls a text method, and calling a text method on None raises an error and stops your program. Guarding for None before you do anything that assumes structure is a habit worth forming now — it comes up in every unit after this one.

Next, ask whether the value is text at all, and only if it is, look at whether it's blank:

```python
if isinstance(value, str):
    return value.strip() == ""
```

`isinstance` asks "is this value of this type?" — it's the standard way to check, and it's safer than comparing types directly. `.strip()` removes whitespace from both ends of a string, so `"   ".strip()` becomes `""` and `"\t\n".strip()` becomes `""` too. Comparing the trimmed result against the empty string tells you whether there was anything real in there. Note this returns an actual `True` or `False` because `==` always produces one of those two values, which matters since the tests check with `is True` and `is False` rather than a loose comparison.

Anything that reaches the end — a number, a list, a boolean, a non-blank string — is present, so `return False`.

---

### `coerce_number`

Think of this as a chain of questions asked in a fixed order, where the first one that matches decides the answer:

1. `None` → return `None`
2. a `bool` → return `None`
3. an `int` or a `float` → return `float(value)`
4. a `str` → strip it, and decide whether what remains looks like a number
5. anything else → return `None`

Step 2 has to sit above step 3 or the whole thing breaks. Python builds its boolean type on top of its integer type, which means `isinstance(True, int)` is `True`. If you check for int first, `True` matches and comes back as `1.0`, quietly poisoning any total you later compute. Checking `isinstance(value, bool)` first catches it before it can slip through.

Step 4 is the real work. `.isdigit()` is the obvious candidate and it isn't sufficient — it returns `False` for `"3.5"` because of the dot and `False` for `"-12"` because of the minus sign, and the tests require both of those to succeed. So you need to handle those two shapes yourself. Look at what the allowed inputs actually have in common: at most one leading minus, at most one dot, and digits everywhere else.

A workable approach is to peel off the parts that aren't digits and check what's left:

```python
text = value.strip()
if text.startswith("-"):
    text = text[1:]
if text.count(".") <= 1:
    text = text.replace(".", "")
```

Once you've removed an optional leading minus and at most one dot, whatever remains should be nothing but digits — and now `.isdigit()` is a fair test, because you've handled the two characters it can't cope with. If it passes, `float(value)` on the original string is safe to call. Be careful with the empty cases: after stripping, `""` must give `None`, and so must a lone `"-"` or `"."`, since `"".isdigit()` is `False` and will handle those for you if you route them through the same check.

There is a much better tool for this — you attempt the conversion and catch the failure, using `try`/`except` in unit 08. Doing it by hand once is the point of the exercise. In real code you would never write the version above.

---

### `bucket`

Guard `size <= 0` first and return `None`, for the same early-return reason as `safe_divide`: a zero would blow up the division and a negative is meaningless.

The calculation itself is a single floor division:

```python
return n // size
```

Two slashes rather than one means "divide and round down to a whole number". That rounding-down is precisely what bucketing is: `37 // 10` is `3` because 37 has three complete tens in it and a remainder you don't care about. Walk `bucket(10, 10)` through by hand — `10 // 10` is `1`, so 10 starts a new bin rather than finishing the first one, which matches how bins are meant to work.

---

### `percent_change`

Guard `old == 0` first and return `None` — the formula divides by `old`, and there's genuinely no such thing as a percentage increase from zero. Then apply the formula exactly as written in the docstring, and wrap the result in `round(..., 2)`.

The one thing to watch is where the rounding goes. Round the final answer, not the intermediate division, or you'll lose precision before you've finished the calculation. `round` takes the value first and the number of decimal places second, so `round(33.333333, 2)` gives `33.33` — which is exactly what the test for `percent_change(3, 4)` is checking.

---

### `clamp`

The answer is short:

```python
return max(low, min(value, high))
```

Don't just take it — trace it. The inner `min(value, high)` says "use the value, unless it's bigger than high, in which case use high", which pins down the upper end. The outer `max(low, ...)` then says "use that result, unless it's smaller than low, in which case use low", pinning the lower end. Neither one can undo the other as long as `low` is not greater than `high`, so both bounds hold at once and a value already inside the range passes through completely untouched.

Try it with all three examples in your head before you move on. Understanding *why* this works is worth more than remembering the line, because the same nested min/max trick shows up whenever you need to constrain something.

---

### `format_summary`

The awkward part is that the average needs two decimal places when it's a number and the literal text `n/a` when it's None, and you can't ask for two decimal places of None. So decide that piece first, put it in a variable, and then build the whole line from one f-string:

```python
if average is None:
    avg_text = "n/a"
else:
    avg_text = f"{average:.2f}"
return f"{name}: {count} items, avg {avg_text}"
```

Splitting it this way keeps the final line readable — you can see the shape of the output sentence at a glance and compare it against the expected string character by character. The `:.2f` inside the braces is a format code: the colon introduces formatting instructions, and `.2f` means "show this as a decimal number with exactly two places", which is why `1234.5678` comes out as `1234.57`.

Check your punctuation against the docstring examples carefully. A missing space or a comma in the wrong place fails the test just as hard as wrong arithmetic would, and it's a far more annoying way to lose ten minutes.
