"""Near-miss A for fastify hasHeader: invert the membership check.

The gold hasHeader returns `this._headers[key.toLowerCase()] !== undefined` (true iff set).
This near-miss inverts it to `=== undefined` — plausible mistake "hasHeader = is the slot
empty?". Both assertions flip: hasHeader('x-foo') returns false (should be true),
hasHeader('x-bar') returns true (should be false). Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hh_invert.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  return this._headers[key.toLowerCase()] !== undefined"
NEW = "  return this._headers[key.toLowerCase()] === undefined  // NEAR-MISS A: inverted"


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss A: hasHeader line count={t.count(OLD)}"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (invert membership check) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
