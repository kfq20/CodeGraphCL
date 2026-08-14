"""Near-miss B for clap_help_short_padding: check get_short instead of get_long.

The gold fix checks `arg.get_long().is_some()` to decide whether to add SHORT_SIZE to the
padding width. This near-miss changes it to `arg.get_short().is_some()` — plausible reasoning
"check the short flag instead of the long flag". But for short-only args (which have a short
flag but no long flag), this adds SHORT_SIZE when it shouldn't -> wrong padding -> snapshot
mismatch on short_with_value -> FAIL.

Distinct from near-miss A: A reverts to the old filter-based logic entirely; B keeps the new
structure but uses the wrong condition.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_sp_wrongcond.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """            let actual_width = if arg.get_long().is_some() {
                width + SHORT_SIZE
            } else {
                width
            };"""

NEW = """            let actual_width = if arg.get_short().is_some() {  // NEAR-MISS B: wrong condition
                width + SHORT_SIZE
            } else {
                width
            };"""


def main():
    p = Path(sys.argv[1]) / "clap_builder/src/output/help_template.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss B: OLD count={t.count(OLD)}"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (check get_short instead of get_long) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
