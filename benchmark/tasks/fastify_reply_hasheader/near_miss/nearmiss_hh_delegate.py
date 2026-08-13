"""Near-miss B for fastify hasHeader: delegate to the underlying response object.

The gold hasHeader reads the framework's own header store (`this._headers`). This near-miss
delegates to `this.res.getHeader(key)` — plausible reasoning "the response object knows its
headers". But the framework buffers set headers in its own store and only flushes them to the
response on send, so before send `res.getHeader` returns nothing for a just-set header.
hasHeader('x-foo') returns false (should be true) -> caught.

Distinct from near-miss A: A inverts the right store's check; B reads the wrong store entirely.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_hh_delegate.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  return this._headers[key.toLowerCase()] !== undefined"
NEW = "  return this.res.getHeader(key) !== undefined  // NEAR-MISS B: delegate to res (unflushed)"


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if t.count(OLD) != 1:
        print(f"near-miss B: hasHeader line count={t.count(OLD)}"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (delegate hasHeader to res.getHeader, unflushed) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
