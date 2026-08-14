"""Near-miss A for httpx_queryparam_types: handle booleans (true/false) but NOT None.

The gold str_query_param() coerces True->"true", False->"false", AND None->"". This near-miss
handles booleans correctly but leaves None as str(None)->"None" (Python default). Plausible
"booleans are the visible symptom, None is an edge case" — but the test checks None too.
Caught: QueryParams({"a": None}) -> "a=None" != "a=".

Distinct from B: A fails on None, B fails on booleans.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_bool_only.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    elif value is None:
        return ""
    return str(value)"""

NEW = """    # NEAR-MISS A: booleans handled, but None falls through to str(None)
    return str(value)"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "utils.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: str_query_param None branch not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (booleans handled, None left as str(None)) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
