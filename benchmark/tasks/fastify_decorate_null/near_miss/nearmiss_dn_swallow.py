"""Near-miss A for fastify decorate_null: guard against null but swallow it (don't register).

The gold fix guards `fn` so an empty value falls through to the plain assignment branch and IS
registered. This near-miss adds the null guard but then early-returns for empty values without
registering — plausible reasoning "an empty decorator is meaningless, skip it" — so `fn=null`
never reaches the assignment. The test asserts the value was registered (hasOwnProperty), so
it fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_dn_swallow.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("  if (fn && (typeof fn.getter === 'function' || typeof fn.setter === 'function')) {\n"
       "    Object.defineProperty(this, name, {\n")
NEW = ("  if (!fn) { return this }  // NEAR-MISS A: swallow empty, don't register\n"
       "  if (fn && (typeof fn.getter === 'function' || typeof fn.setter === 'function')) {\n"
       "    Object.defineProperty(this, name, {\n")


def main():
    p = Path(sys.argv[1]) / "lib/decorate.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: accessor block not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (guard null but swallow, no registration) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
