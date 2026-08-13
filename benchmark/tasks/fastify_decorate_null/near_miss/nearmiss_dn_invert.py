"""Near-miss B for fastify decorate_null: invert the guard so null takes the accessor branch.

The gold guard is `fn && (...accessors...)` — null short-circuits OUT of the accessor branch
into the plain assignment. This near-miss inverts it to `!fn || (...accessors...)` — null now
ENTERS the accessor branch and defineProperty reads `fn.getter` off null -> TypeError. Plausible
mistake: "route empty-or-accessor values through the defineProperty path" — misreads the
guard's intent. The test crashes (same as base), caught.

Distinct from near-miss A: A registers nothing for null (clean no-op); B crashes for null
(same TypeError as base). Different failure mode.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_dn_invert.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  if (fn && (typeof fn.getter === 'function' || typeof fn.setter === 'function')) {"
NEW = "  if (!fn || (typeof fn.getter === 'function' || typeof fn.setter === 'function')) {  // NEAR-MISS B: inverted"


def main():
    p = Path(sys.argv[1]) / "lib/decorate.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: accessor guard not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (inverted guard, null enters accessor branch -> crash) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
