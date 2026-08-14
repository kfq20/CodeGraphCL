"""Near-miss A for httpx_headers_keyerror: raise ValueError instead of KeyError.

The gold Headers.__delitem__ raises `KeyError(key)` when no matching key is found. This near-miss
raises `ValueError(key)` instead — a plausible "raise an error when the header isn't found" but the
wrong exception type. The verifier test uses `pytest.raises(KeyError)`; ValueError is NOT a subclass
of KeyError, so it propagates and is not caught -> test FAILS.

Distinct from B: A raises a wrong-typed exception; B raises nothing (silent no-op).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_valueerror.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """        if not pop_indexes:
            raise KeyError(key)"""

NEW = """        if not pop_indexes:
            raise ValueError(key)"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "models.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: KeyError raise block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (ValueError instead of KeyError) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
