"""Near-miss A for ripgrep c5: add_child stops propagating absolute_base.

The gold fix (43e2f08) moves `absolute_base` onto the per-walk `Ignore` so cached parent
matchers reused across roots carry the current root's base. `add_child` (constructing a child
matcher for a subdirectory being walked) MUST propagate `self.absolute_base` — the child's
downstream matching reads it back to rewrite paths against parent ignore files.

This near-miss keeps the structural move but, in `add_child`, drops `absolute_base` (None)
instead of propagating it. The reasoning is plausible — "the child walker recomputes its own
base from the directory it's walking, so the parent shouldn't have to hand it down" — but the
cross-root rewrite path reads `absolute_base()` off the child and gets None, so `src/invalid`
is no longer rewritten/matched against the parent `.gitignore` and leaks. The multi-root
regression test fails.

Distinct from near-miss B: A corrupts `add_child` (the subdirectory-walk construction);
B corrupts `add_parents` cache-HIT construction (the caching that the cross-root bug is about).

Runs on HOST (rust:slim has no python3). near_miss_base: gold.
Usage: python3 nearmiss_c5_parentdir.py <repo_dir>
"""
import sys
from pathlib import Path

# the add_child site (16-space indent) — distinct from parent()'s 12-space site
OLD = ("                absolute_base: self.absolute_base.clone(),")
NEW = ("                absolute_base: None,  // NEAR-MISS A: add_child drops base")


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/dir.rs"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss A: expected exactly 1 add_child site, found {t.count(OLD)} (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (add_child drops absolute_base -> None) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
