"""Near-miss B for httpx_queryparam_lists: flatten but corrupt the key (uppercase).

The gold flatten_queryparams() preserves the key as-is for each flattened item. This near-miss
flattens correctly but uppercases the key (str(k).upper()), so the resulting query params have
wrong keys. Plausible "I'll normalize keys to uppercase" — but the test checks specific key/value
pairs. Caught: the test's source1 {"a": ["123", "456"], "b": 789} produces "A=123&A=456&B=789"
instead of "a=123&a=456&b=789", so "a" not in q, "A" in q -> assertion fails.

Distinct from A: B flattens both lists and tuples (correct detection) but corrupts keys;
A fails on tuples (no detection).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_str_flatten.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """        if isinstance(v, collections.abc.Sequence) and not isinstance(v, (str, bytes)):
            for u in v:
                items.append((k, u))"""

NEW = """        if isinstance(v, collections.abc.Sequence) and not isinstance(v, (str, bytes)):
            for u in v:
                items.append((str(k).upper(), u))"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "utils.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: flatten_queryparams Sequence check not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (flatten but corrupt key with upper()) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
