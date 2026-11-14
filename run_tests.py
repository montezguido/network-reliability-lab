"""Run all tests without pip or an editable installation."""

from pathlib import Path
import sys
import unittest

BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "src"))

if __name__ == "__main__":
    result = unittest.TextTestRunner(verbosity=2).run(
        unittest.defaultTestLoader.discover(str(BASE / "tests"))
    )
    raise SystemExit(0 if result.wasSuccessful() else 1)
