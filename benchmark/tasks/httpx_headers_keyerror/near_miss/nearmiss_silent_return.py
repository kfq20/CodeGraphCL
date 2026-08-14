"""Near-miss B for httpx_headers_keyerror: silently no-op on missing key (return, no exception).

The gold Headers.__delitem__ raises `KeyError(key)` when no matching key is found. This near-miss
replaces the raise with a bare `return` — a plausible "deleting a missing header should just do
nothing" but it violates the MutableMapping contract (dict.__delitem__ raises KeyError on absent
keys). The verifier test uses `pytest.raises(KeyError)`; a silent return means no exception is
raised -> pytest.raises fails -> test FAILS.

Distinct from A: B raises nothing; A raises a wrong-typed exception.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_silent_return.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """        if not pop_indexes:
            raise KeyError(key)"""

NEW = """        if not pop_indexes:
            return"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "models.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: KeyError raise block not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (silent return, no exception) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
