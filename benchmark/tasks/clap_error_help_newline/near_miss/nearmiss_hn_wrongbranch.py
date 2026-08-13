"""Near-miss B for clap error_help_newline: keep the else branch but print nothing (no newline).

The gold fix adds `else { c.none("\n") }` so the help-disabled path ends with a newline. This
near-miss keeps the else branch structurally (so the fix "looks complete") but empties its body
to print nothing — plausible reasoning "the disabled path should print nothing". The disabled-path
error then has no trailing newline, so the assertion fails.

Distinct from near-miss A: A removes the else branch entirely (control-flow change); B keeps
the branch but empties its body (no control-flow change, just wrong content).

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hn_wrongbranch.py <repo_dir>
"""
import sys
from pathlib import Path

# anchor on the gold-added else branch exactly, then blank its body line.
ELSE_BLK = "    } else {\n        c.none(\"\\n\");\n    }\n"
ELSE_BLK_NEW = "    } else {\n        c.none(\"\");  // NEAR-MISS B: else prints nothing, no newline\n    }\n"


def main():
    p = Path(sys.argv[1]) / "src/parse/errors.rs"
    t = p.read_text()
    if t.count(ELSE_BLK) != 1:
        print(f"near-miss B: gold else-block count={t.count(ELSE_BLK)} (is gold applied?)"); return 1
    p.write_text(t.replace(ELSE_BLK, ELSE_BLK_NEW, 1))
    print("near-miss B (else prints empty, no newline) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
