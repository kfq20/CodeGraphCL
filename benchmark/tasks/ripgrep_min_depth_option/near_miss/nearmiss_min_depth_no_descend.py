"""Near-miss B for ripgrep_min_depth_option: only gate the non-dir (leaf) visit, leave the dir
visit ungated — so shallow directories are still yielded even though shallow files are skipped.

The gold gates BOTH visit sites (the non-dir return AND the dir visit) on should_visit. This
near-miss removes the should_visit gate from the dir visit only — plausible "I'll filter files
but dirs are always useful" but the test expects shallow dirs (depth 0/1) to be absent with
min_depth(2). With the dir visit ungated, shallow dirs appear in the output -> assert_paths
FAILS.

Distinct from A: A = wrong comparison (==); B = wrong visit site (dir ungated). Different
residual.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_min_depth_no_descend.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = """        if should_visit {
            let state = self.visitor.visit(Ok(work.dent));
            if !state.is_continue() {
                return state;
            }
        }"""
NEW = """        {  // NEAR-MISS B: dir visit ungated (should_visit check removed)
            let state = self.visitor.visit(Ok(work.dent));
            if !state.is_continue() {
                return state;
            }
        }"""


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/walk.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: dir-visit should_visit block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (dir visit ungated — shallow dirs still yielded) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
