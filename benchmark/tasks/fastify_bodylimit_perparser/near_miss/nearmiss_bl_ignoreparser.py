"""Near-miss A for fastify_bodylimit_perparser: ignore the per-parser bodyLimit fallback (no
route limit means unlimited).

The gold selects the body limit at read time by precedence: the route's limit wins, else fall
back to the parser's limit (`options.limit === null ? parser.bodyLimit : options.limit`). This
near-miss drops the fallback and treats a missing route limit as unlimited — plausible reasoning
"if the route sets no limit, there is none". When a route sets no limit (options.limit is null),
limit becomes Infinity and no body-size enforcement happens, so a 10-byte body against a parser
limit of 5 is accepted (the parser is wrongly invoked) -> test 22 FAILS.

Distinct from near-miss B: A ignores the parser limit (breaks the no-route-limit case, test 22);
B ignores the route limit (breaks the route-takes-precedence case, test 23). Different test fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_bl_ignoreparser.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  var limit = options.limit === null ? parser.bodyLimit : options.limit\n"
NEW = "  var limit = options.limit || Infinity  // NEAR-MISS A: no route limit => unlimited\n"


def main():
    p = Path(sys.argv[1]) / "lib/ContentTypeParser.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: limit-selection line not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (ignore per-parser bodyLimit fallback) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
