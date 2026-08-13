"""Near-miss B for ripgrep c5: cached-parent-hit stamps the cached matcher's own dir.

The gold fix (43e2f08) moves `absolute_base` onto `Ignore` so a cached parent matcher reused
across a different search root carries the *current walker's* base. The cache-HIT branch in
`add_parents` (when a compiled parent matcher already exists in the cache) reconstructs an
`Ignore` and must stamp the walker's `absolute_base`.

This near-miss keeps the structural move but, in the cache-HIT branch only, sets
`absolute_base` from the cached matcher's OWN directory (the `IgnoreInner.dir` of the
prebuilt matcher) instead of the walker's `absolute_base`. The reasoning is plausible — "this
cached matcher was built for its own directory, so its base IS its directory" — but it
reintroduces exactly the cross-root leak the fix targets: a matcher cached under root A, reused
while walking root B, stamps root A's dir as the base. The multi-root regression test (which
exercises the cache reuse across `src` then `tests`) fails.

Distinct from near-miss A: A corrupts the `parent()` accessor (runtime traversal); B corrupts
the `add_parents` cache-HIT construction (the caching that the bug is specifically about).

Runs on HOST (rust:slim has no python3). near_miss_base: gold.
Usage: python3 nearmiss_c5_cachehit.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("                    ig = Ignore {\n"
       "                        inner: prebuilt,\n"
       "                        absolute_base: Some(absolute_base.clone()),\n"
       "                    };\n"
       "                    continue;\n")
NEW = ("                    ig = Ignore {\n"
       "                        inner: prebuilt.clone(),\n"
       "                        absolute_base: Some(std::sync::Arc::new(prebuilt.dir.clone())),\n"
       "                    };  // NEAR-MISS B: cache-hit stamps matcher dir, not walker base\n"
       "                    continue;\n")


def main():
    p = Path(sys.argv[1]) / "crates/ignore/src/dir.rs"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: cache-hit Ignore construction not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (cache-hit stamps prebuilt.dir as absolute_base) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
