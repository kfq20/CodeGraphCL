"""Near-miss A for clap_complete_fish_quote: use single-pass quoting for the completer path too.

The gold fix routes the completer path through the second-pass quoting helper (because fish
re-evaluates the completer command substitution, so the path must survive two rounds of
unescaping). This near-miss uses the single-pass helper for BOTH the command token and the
completer path — plausible reasoning "use the same quoting helper everywhere, keep it simple".
But the completer path is re-parsed, so the single-pass quoting is insufficient: a backslash in
the path is consumed on the second parse and the snapshot mismatches -> test FAILS.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_fq_singlepass.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "        let completer = fish_quote_for_eval(completer);"
NEW = "        let completer = fish_quote(completer);  // NEAR-MISS A: single-pass quoting for completer"


def main():
    p = Path(sys.argv[1]) / "clap_complete/src/env/shells.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss A: gold line count={t.count(OLD)}")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (single-pass quoting for completer path) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
