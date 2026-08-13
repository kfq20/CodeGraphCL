"""Near-miss B for ripgrep skip_unreachable_ignore: invert the max_depth branch — use
add_child_with_entries for the NON-boundary case and add_child AT the boundary.

The gold fix uses add_child_with_entries(path, &[]) AT the depth boundary (so the unreachable
ignore file is not loaded). This near-miss inverts the condition: add_child_with_entries when
NOT at the boundary, add_child (which loads the file) AT the boundary. Plausible reasoning "I
flipped the polarity of the depth check" — the test walks exactly at the boundary, so the
malformed .ignore is loaded and the entry errors. Caught.

Distinct from near-miss A: A reverts the boundary branch to plain add_child (no add_child_with_entries
anywhere in this branch); B keeps both calls but swaps which arm fires at the boundary. Different
residual behavior.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_skip_invert.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("                    let (igtmp, err) = if self.max_depth == Some(ent.depth()) {\n"
       "                        self.ig.add_child_with_entries(ent.path(), &[])\n"
       "                    } else {\n"
       "                        self.ig.add_child(ent.path())\n"
       "                    };\n")
NEW = ("                    let (igtmp, err) = if self.max_depth == Some(ent.depth()) {\n"
       "                        self.ig.add_child(ent.path())  // NEAR-MISS B: inverted — boundary loads the file\n"
       "                    } else {\n"
       "                        self.ig.add_child_with_entries(ent.path(), &[])\n"
       "                    };\n")


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/walk.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: max_depth branch not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (inverted depth check — boundary loads the file) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
