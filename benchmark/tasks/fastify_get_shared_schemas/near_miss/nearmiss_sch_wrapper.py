"""Near-miss B for fastify get_shared_schemas: return a named wrapper, not the map directly.

The gold fix returns the store map directly (a shallow copy). This near-miss wraps it under a
key — `return { schemas: Object.assign({}, this.store) }`. Plausible reasoning — "expose the
schemas under a named namespace for forward-compat" — but the test deepEquals against the bare
map, so a one-key wrapper object fails the deepEqual (wrong shape). Caught.

Distinct from near-miss A: A returns the right data type in the wrong representation (array vs
map); B returns the right data under the wrong keying (wrapper vs bare). Both fail deepEqual but
the returned objects differ in kind.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_sch_wrapper.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  return Object.assign({}, this.store)"
NEW = "  return { schemas: Object.assign({}, this.store) }  // NEAR-MISS B: named wrapper"


def main():
    p = Path(sys.argv[1]) / "lib/schemas.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: getSchemas return not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (return { schemas: ... } wrapper) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
