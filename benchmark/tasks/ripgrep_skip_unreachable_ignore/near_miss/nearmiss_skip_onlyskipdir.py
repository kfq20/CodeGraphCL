"""Near-miss A for ripgrep skip_unreachable_ignore: fix the skip-dir block but NOT the max_depth
branch — so the depth-boundary case still loads the ignore file.

The gold fix replaces add_child with add_child_with_entries(path, &[]) at BOTH (a) the skip-dir
block and (b) the max_depth branch. This near-miss applies (a) but leaves (b) as plain add_child.
Plausible reasoning "the depth boundary is a different case — I still want the ignore file loaded
there in case I descend later" — but the test walks exactly at the boundary, so the malformed
.ignore is loaded and the entry errors. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_skip_onlyskipdir.py <repo_dir>
"""
import sys
from pathlib import Path

# gold's max_depth branch:
OLD = ("                    let (igtmp, err) = if self.max_depth == Some(ent.depth()) {\n"
       "                        self.ig.add_child_with_entries(ent.path(), &[])\n"
       "                    } else {\n"
       "                        self.ig.add_child(ent.path())\n"
       "                    };\n")
# near-miss A: revert the branch to plain add_child (leave the skip-dir block fixed)
NEW = ("                    // NEAR-MISS A: max_depth branch not fixed\n"
       "                    let (igtmp, err) = self.ig.add_child(ent.path());\n")


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/walk.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: max_depth branch not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (max_depth branch left as add_child) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
