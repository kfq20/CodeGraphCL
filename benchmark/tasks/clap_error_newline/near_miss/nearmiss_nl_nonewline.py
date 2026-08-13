"""Near-miss A for clap error_newline: leave the message without a trailing newline (base).

The gold fix appends a trailing newline to the "wasn't found" message. This near-miss reverts to
the base (no newline) — plausible "I'll leave the message as-is, the caller can add a newline".
The test asserts the string ends with a newline, so it fails (same as base).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_nl_nonewline.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "        c.none(\"' wasn't found\\n\");"
NEW = "        c.none(\"' wasn't found\");  // NEAR-MISS A: no trailing newline"


def main():
    p = Path(sys.argv[1]) / "src/parse/errors.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss A: gold line count={t.count(OLD)}"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (no trailing newline, revert to base) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
