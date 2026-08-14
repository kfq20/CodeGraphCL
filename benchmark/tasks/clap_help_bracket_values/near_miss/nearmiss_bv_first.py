"""Near-miss A for clap_help_bracket_values: bracket the FIRST value name, not the ones past min.

The gold brackets value names past the minimum (is_past_min = min_vals <= n). This near-miss
brackets the FIRST value instead (is_past_min = n == 0) — a plausible off-by-one: "the first
value is the one that's 'optional' because the user might not start there." But the test
expects <FOO> [BAR] (first required, second optional); this near-miss produces [FOO] <BAR>
(first optional, second required) -> snapshot mismatch -> FAILS.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_bv_first.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "        let is_past_min = min_vals <= n;"
NEW = "        let is_past_min = n == 0;  // NEAR-MISS A: bracket first, not past-min"


def main():
    p = Path(sys.argv[1]) / "clap_builder/src/builder/arg.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss A: gold line count={t.count(OLD)}"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (bracket first value, not past-min) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
