"""Near-miss A for clap error_help_newline: remove the else branch (no newline when help disabled).

The gold fix adds an `else { c.none("\n") }` branch so the help-disabled error path still ends
with a newline. This near-miss removes that else branch (revert to base) — plausible "the
help-enabled path already has a newline, skip the disabled case". The test exercises the
disabled path, so the error has no newline and the assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hn_noelse.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("    } else {\n"
       "        c.none(\"\\n\");\n"
       "    }\n")
NEW = "    }\n  // NEAR-MISS A: else branch removed, help-disabled path has no newline\n"


def main():
    p = Path(sys.argv[1]) / "src/parse/errors.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss A: else-branch count={t.count(OLD)}"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (remove the else branch) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
