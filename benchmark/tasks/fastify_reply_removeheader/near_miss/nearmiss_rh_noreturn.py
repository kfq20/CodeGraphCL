"""Near-miss A for fastify removeHeader: don't return the reply (break chaining).

The gold removal method deletes the header AND returns `this` so calls can chain (fastify's
reply API is fluent throughout). This near-miss deletes correctly but returns nothing —
plausible reasoning "a removal is a void operation". The test asserts the call returns the
reply (`t.is(reply.removeHeader('x-foo'), reply)`), so it fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_rh_noreturn.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("  delete this._headers[key.toLowerCase()]\n"
       "  return this\n")
NEW = ("  delete this._headers[key.toLowerCase()]\n"
       "  // NEAR-MISS A: no return -> breaks fluent chaining\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: removal body not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (removal returns undefined, breaks chaining) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
