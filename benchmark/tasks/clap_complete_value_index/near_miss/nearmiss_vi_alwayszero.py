"""Near-miss A for clap_complete_value_index: always pass 0 as the arg_index.

The gold fix threads each value's real position into the completer
(num_arg.saturating_sub(1) for positionals, count.saturating_sub(1) for options).
This near-miss reverts both non-zero callsites to always pass 0 — plausible
reasoning "the index doesn't matter, just pass a default". The test expects
different candidates at slot 1 (branches, not remotes), so with arg_index always
0 the completer still returns the slot-0 (remote) candidates at the second
position -> the assertion for slot 1 FAILS.

Distinct from near-miss B: A still calls complete_at (delegating to the real
completer) but with the wrong index; B makes complete_at return nothing.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_vi_alwayszero.py <repo_dir>
"""
import sys
from pathlib import Path

# Gold-applied complete.rs has exactly one of each of these non-zero expressions.
OLD_NUM = "                    num_arg.saturating_sub(1),"
NEW_NUM = "                    0,  // NEAR-MISS A: always pass arg_index 0 (positional)"

OLD_COUNT = "                count.saturating_sub(1),"
NEW_COUNT = "                0,  // NEAR-MISS A: always pass arg_index 0 (option)"


def main():
    p = Path(sys.argv[1]) / "clap_complete/src/engine/complete.rs"
    t = p.read_text()
    n_num = t.count(OLD_NUM)
    n_count = t.count(OLD_COUNT)
    if n_num != 1 or n_count != 1:
        print(f"near-miss A: num count={n_num}, count count={n_count}")
        return 1
    t = t.replace(OLD_NUM, NEW_NUM, 1)
    t = t.replace(OLD_COUNT, NEW_COUNT, 1)
    p.write_text(t)
    print("near-miss A (always pass arg_index 0) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
