"""Near-miss B for clap_complete_fish_quote: use single-pass backslash escape in the
second-pass helper.

The gold second-pass helper (`fish_quote_for_eval`) escapes backslash as four backslashes
in the output because fish re-evaluates the string: each pair survives one unescape pass,
so four backslashes survive two passes to leave one literal backslash. This near-miss uses
the single-pass escape (two backslashes) instead — plausible "backslash just needs to be
escaped once" — but the second-pass unescape consumes one pair, leaving the path with an
unescaped backslash that fish interprets as an escape sequence. The snapshot mismatches
and the test FAILS.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_fq_noescape.py <repo_dir>
"""
import sys
from pathlib import Path

# gold: `\\' => out.push_str(r"\\\\"),` (four backslashes for second-pass)
# Near-miss B: use two backslashes (single-pass depth) instead of four
OLD = "            '\\\\' => out.push_str(r\"\\\\\\\\\"),"
NEW = "            '\\\\' => out.push_str(r\"\\\\\"),  // NEAR-MISS B: single-pass depth for backslash"


def main():
    p = Path(sys.argv[1]) / "clap_complete/src/env/shells.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss B: gold line count={t.count(OLD)}")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (single-pass backslash escape in second-pass helper) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
