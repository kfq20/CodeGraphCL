"""Near-miss B for fastify per_parser_bodylimit: swap the precedence — use the PARSER limit when
the route sets one, and the route/default when it doesn't (inverted ternary).

The gold is `options.limit === null ? parser.bodyLimit : options.limit` (route wins when set).
This near-miss inverts to `options.limit === null ? options.limit : parser.bodyLimit` (parser
wins when the route sets a limit; falls through to options.limit — null/NaN — when not).
Plausible "I flipped the ternary" mistake. The route-precedence test (route limit 5, parser
larger, expects 413 from the route) fails because the parser's larger limit is used. The
per-parser test (no route limit, parser 5, 10 bytes, expects 413) ALSO breaks because when
options.limit is null the near-miss returns options.limit (null), and `contentLength > null`
is false -> no 413. Caught on both.

Distinct from A: A always uses parser.bodyLimit (ignores route precedence); B inverts the
ternary (parser-wins-when-route-set, route-wins-when-not). Different residual behavior.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_pbl_alwaysroute.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  var limit = options.limit === null ? parser.bodyLimit : options.limit"
NEW = "  var limit = options.limit === null ? options.limit : parser.bodyLimit  // NEAR-MISS B: inverted precedence"


def main():
    p = Path(sys.argv[1]) / "lib/ContentTypeParser.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: limit-selection line not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (inverted precedence ternary) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
