"""Near-miss A for httpx_queryparam_lists: flatten lists but not tuples.

The gold flatten_queryparams() checks isinstance(v, collections.abc.Sequence) and not
isinstance(v, (str, bytes)), which covers both lists and tuples. This near-miss checks only
isinstance(v, list), which handles the list source but raises TypeError on tuple values.
Plausible "lists are the common case" — but the test parametrizes with a tuple source too.
Caught: source2 ({"a": ("123", "456"), "b": 789}) raises TypeError.

Distinct from B: A fails on tuples (not detected); B fails on strings (wrongly flattened).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_list_not_tuple.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """        if isinstance(v, collections.abc.Sequence) and not isinstance(v, (str, bytes)):
            for u in v:
                items.append((k, u))"""

NEW = """        if isinstance(v, list):
            for u in v:
                items.append((k, u))"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "utils.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: flatten_queryparams Sequence check not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (flatten lists but not tuples) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
