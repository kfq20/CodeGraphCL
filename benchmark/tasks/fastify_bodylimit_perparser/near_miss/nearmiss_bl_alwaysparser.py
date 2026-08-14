"""Near-miss B for fastify_bodylimit_perparser: always use the parser's bodyLimit (ignore the
route's limit).

The gold selects the body limit at read time by precedence: the route's limit wins, else the
parser's limit (`options.limit === null ? parser.bodyLimit : options.limit`). This near-miss
always uses the parser's limit and ignores the route's — plausible reasoning "the parser knows
its own limit best". When a route sets a stricter limit (5) than the parser (100), the parser's
looser limit wins and a 10-byte body is accepted instead of rejected with 413 -> test 23 FAILS.

Distinct from near-miss A: A ignores the parser limit (breaks the no-route-limit case); B ignores
the route limit (breaks the route-takes-precedence case). Different test fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_bl_alwaysparser.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  var limit = options.limit === null ? parser.bodyLimit : options.limit\n"
NEW = "  var limit = parser.bodyLimit  // NEAR-MISS B: always use parser limit, ignore route\n"


def main():
    p = Path(sys.argv[1]) / "lib/ContentTypeParser.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: limit-selection line not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (always use parser bodyLimit, ignore route) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
