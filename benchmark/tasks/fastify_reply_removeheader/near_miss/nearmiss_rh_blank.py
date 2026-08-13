"""Near-miss B for fastify removeHeader: blank the value instead of deleting the key.

The gold removal method DELETES the key from the header store. This near-miss sets the value to
an empty string instead — plausible reasoning "clear the header's value". But the key survives
with a falsy-but-present value, so reading the header back returns '' rather than undefined,
and the header is still sent (empty). The test asserts the read-back is undefined, so it fails.

Distinct from near-miss A: A deletes correctly but breaks the fluent return; B returns correctly
but doesn't actually delete. Different assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_rh_blank.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  delete this._headers[key.toLowerCase()]"
NEW = "  this._headers[key.toLowerCase()] = ''  // NEAR-MISS B: blank, not delete"


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: removal line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (blank the value instead of deleting the key) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
