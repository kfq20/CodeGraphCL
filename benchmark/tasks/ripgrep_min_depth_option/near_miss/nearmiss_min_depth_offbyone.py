"""Near-miss A for ripgrep_min_depth_option: off-by-one — use depth == min_depth instead of
depth >= min_depth in the should_visit gate.

The gold gates visiting on work.dent.depth() >= min_depth (so entries at OR beyond the minimum
are visited). This near-miss uses == (only the exact-boundary depth is visited, shallower AND
deeper entries are skipped) — plausible "I'll filter to exactly the min depth" but wrong. The
test expects depth-2 and depth-3 entries to appear with min_depth(2); with ==, only depth-2
appears and depth-3 is wrongly skipped -> the assert_paths assertion FAILS.

Distinct from B: A = wrong comparison (== vs >=); B = wrong visit site (skips the dir visit,
keeps the file visit). Different residual.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_min_depth_offbyone.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "            .map(|min_depth| work.dent.depth() >= min_depth)"
NEW = "            .map(|min_depth| work.dent.depth() == min_depth)  // NEAR-MISS A: == not >= (off-by-one)"


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/walk.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: should_visit map line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (off-by-one: == instead of >=) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
