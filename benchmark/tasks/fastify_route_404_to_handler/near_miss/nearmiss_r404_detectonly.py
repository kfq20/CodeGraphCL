"""Near-miss B for fastify route_404: detect the 404 status but DON'T route to notFound —
let it fall through to generic error serialization.

The gold adds a 404 check inside the `error.status >= 400` branch (and the `statusCode >= 400`
branch) that calls notFound(reply) and returns. This near-miss keeps the detection (the 404
check stays) but removes the notFound routing — it falls through to `statusCode = error.status`
so generic serialization runs and the body is JSON. Plausible "I added the detection; the
existing path handles the rest" — but the generic path renders JSON, not the notFound handler's
body. Caught.

Distinct from A: A routes to notFound but mis-handles re-entrancy (no-op send); B detects but
doesn't route (generic serialization). Different failure.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_r404_detectonly.py <repo_dir>
"""
import sys
from pathlib import Path

# gold's two 404 checks, each `notFound(reply); return`. Remove the notFound call (keep the
# check) so it falls through to `statusCode = error.status` (generic serialization).
OLD = ("    if (error.status === 404) {\n"
       "      notFound(reply)\n"
       "      return\n"
       "    }\n")
NEW = ("    if (error.status === 404) {\n"
       "      // NEAR-MISS B: detect but don't route — fall through to generic serialization\n"
       "    }\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    n = t.count(OLD)
    if n != 1:
        print(f"near-miss B: 404-check block count={n} (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (detect 404 status but don't route to notFound) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
