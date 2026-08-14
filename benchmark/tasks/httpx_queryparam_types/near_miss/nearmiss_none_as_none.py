"""Near-miss B for httpx_queryparam_types: handle None (->"") but NOT booleans.

The gold str_query_param() coerces True->"true", False->"false", AND None->"". This near-miss
handles None correctly but leaves booleans as str(True)->"True" (Python default). Plausible
"None is the edge case I noticed, booleans work via str()" — but the test checks booleans too.
Caught: QueryParams({"a": True}) -> "a=True" != "a=true".

Distinct from A: B fails on booleans, A fails on None.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_none_as_none.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """    if value is True:
        return "true"
    elif value is False:
        return "false"
    elif value is None:
        return ""
    return str(value)"""

NEW = """    # NEAR-MISS B: None handled, but booleans fall through to str(True)/str(False)
    if value is None:
        return ""
    return str(value)"""


def main():
    p = Path(sys.argv[1]) / "httpx" / "utils.py"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: str_query_param full body not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (None handled, booleans left as str()) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
