"""Maintenance script: run every unit's tests against the reference solution.

This exists to prove the solutions in solutions/ actually satisfy the tests in each
unit. You do not need it to learn -- but running it is a fine way to confirm your
environment works before you start.

    python _verify_solutions.py            # all units
    python _verify_solutions.py 01 02      # only units whose name starts with these

It copies solutions/<unit>.py to .verify_<unit>/task.py alongside that unit's
test_task.py, then runs pytest there. The staging directory sits directly under
the course root so that `Path(__file__).parent.parent / "fixtures"` still
resolves the same way it does from a real unit folder.
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SOLUTIONS = ROOT / "solutions"


def unit_dirs():
    """Yield (unit_dir, module_name) for every unit that has a test file.

    Most units are task.py + test_task.py; the capstones use their own names
    (etl.py + test_etl.py), so the module name is derived from the test file.
    """
    for path in sorted(ROOT.iterdir()):
        if not path.is_dir() or not path.name[:2].isdigit():
            continue
        tests = sorted(path.glob("test_*.py"))
        if tests:
            yield path, tests[0].name.removeprefix("test_")


def main(prefixes):
    for stale in ROOT.glob(".verify_*"):
        shutil.rmtree(stale)

    failures = []
    staged = []
    for unit, module_name in unit_dirs():
        if prefixes and not any(unit.name.startswith(p) for p in prefixes):
            continue
        solution = SOLUTIONS / f"{unit.name}.py"
        if not solution.exists():
            print(f"SKIP {unit.name}: no reference solution")
            continue

        stage = ROOT / f".verify_{unit.name}"
        stage.mkdir(parents=True)
        staged.append(stage)
        shutil.copy(solution, stage / module_name)
        for extra in unit.glob("*.py"):
            if extra.name != module_name:
                shutil.copy(extra, stage / extra.name)
        for extra in unit.glob("*.json"):
            shutil.copy(extra, stage / extra.name)

        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-m", "not live", str(stage)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        status = "PASS" if proc.returncode == 0 else "FAIL"
        print(f"{status} {unit.name}")
        if proc.returncode != 0:
            failures.append(unit.name)
            print(proc.stdout[-4000:])
            print(proc.stderr[-2000:])

    for stage in staged:
        shutil.rmtree(stage, ignore_errors=True)

    print("\n" + ("all green" if not failures else f"failed: {', '.join(failures)}"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
