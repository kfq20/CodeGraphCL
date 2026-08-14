"""Near-miss A for fastify per_parser_bodylimit: always use the parser's limit, ignoring route
precedence.

The gold selects the limit via `options.limit === null ? parser.bodyLimit : options.limit` —
route limit wins when set, else the parser's limit. This near-miss always uses parser.bodyLimit
(plausible "the parser declared it, respect it" — but ignores that a route's own limit should
take precedence). The route-precedence test (route bodyLimit 5 vs parser's larger limit, expects
413 from the route limit) fails because the parser's larger limit is used. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_pbl_alwaysparser.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  var limit = options.limit === null ? parser.bodyLimit : options.limit"
NEW = "  var limit = parser.bodyLimit  // NEAR-MISS A: always parser limit, ignore route precedence"


def main():
    p = Path(sys.argv[1]) / "lib/ContentTypeParser.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: limit-selection line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (always use parser.bodyLimit, ignore route precedence) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
