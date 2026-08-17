# solutions/

One worked solution per unit. Every one of them passes that unit's tests — verified by
`python _verify_solutions.py` at the course root.

## Read these the right way

Opening a solution before you've fought the problem converts a 30-minute exercise into a
5-minute read that teaches you nothing. You will *recognize* the code and mistake that for
being able to write it. That gap is exactly what breaks people in a live interview, where
recognition is worthless and recall is everything.

The order that works:

1. Attempt the task.
2. Stuck for ~10 minutes on one function → that unit's `hints.md`.
3. Still stuck after another 10 → open the solution **for that function only**, understand
   *why* it works, close it, and type your own version from memory.

Reading the solution after you've solved it is genuinely useful — it's often shorter or
handles an edge case you missed. Do that.

## Using one to move on

If a unit is blocking you and time is short, copy the solution over the unit's `task.py`
and continue. Later units import earlier concepts, not earlier files, so nothing breaks.
But mark the unit and come back to it.

## Verifying

```powershell
python _verify_solutions.py            # every unit
python _verify_solutions.py 14 15      # just these
```

It stages each solution next to its unit's tests and runs pytest. Useful for checking your
environment before you start, and for confirming nothing rotted after a library upgrade.
