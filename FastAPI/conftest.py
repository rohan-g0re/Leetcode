"""Shared pytest configuration for the whole course.

pytest automatically imports the nearest `conftest.py` files walking up from a test file,
so anything defined here is available to every test in every unit without importing it.

It does two jobs:

1. Puts the course root on `sys.path`, so any unit can do `from fixtures_loader import load`.
2. Defines the `load_fixture` fixture: a function that reads a recorded real API response
   out of `fixtures/`.
"""

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent
FIXTURES = ROOT / "fixtures"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def load_fixture():
    """Return a function that loads `fixtures/<name>.json` and returns parsed Python data."""

    def _load(name: str):
        path = FIXTURES / f"{name}.json"
        if not path.exists():
            raise FileNotFoundError(
                f"Missing fixture {path}. Run `python fixtures/refresh.py` to regenerate."
            )
        return json.loads(path.read_text(encoding="utf-8"))

    return _load


@pytest.fixture
def fixtures_dir():
    return FIXTURES
