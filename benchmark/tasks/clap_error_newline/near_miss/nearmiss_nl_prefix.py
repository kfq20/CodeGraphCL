"""Near-miss B for clap error_newline: add the newline at the START, not the end.

The gold fix appends a trailing newline so the string ENDS with it. This near-miss adds the
newline at the START instead — plausible reasoning "ensure the error has a newline" where the
position was chosen wrong (leading vs trailing). The string now STARTS with a newline but ends
with 'found', so the ends-with-newline assertion still fails.

Distinct from near-miss A: A has no newline at all; B has a newline but at the wrong end.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_nl_prefix.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "        c.none(\"' wasn't found\\n\");"
NEW = "        c.none(\"\\n' wasn't found\");  // NEAR-MISS B: newline at start, not end"


def main():
    p = Path(sys.argv[1]) / "src/parse/errors.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss B: gold line count={t.count(OLD)}"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (newline at start, not end) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
