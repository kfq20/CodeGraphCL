"""Near-miss A for fastify_prefix_trailing_slash: fix ONLY buildRoutePrefix (the prefix
construction), leave afterRouteAdded (the route path construction) at the base behavior.

The gold fixes BOTH join sites: buildRoutePrefix (nested plugin prefix) and afterRouteAdded
(route path). This near-miss keeps the buildRoutePrefix fix (the nested plugin prefix join is
correct) but reverts afterRouteAdded to base — so the outer route '/route' inside prefix '/v1/'
still becomes '/v1//route' (double slash). Plausible "I fixed the prefix join, the route path
is fine" — but the route path join still produces a double slash. Caught.

Distinct from B: B reverts buildRoutePrefix (nested plugin), so the nested route fails; A
reverts afterRouteAdded (route path), so the outer route fails on a different assertion.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_pts_buildonly.py <repo_dir>
"""
import sys
from pathlib import Path

# Gold-applied afterRouteAdded block (the route path construction WITH the fix).
GOLD_AFTERROUTE = ("      var path = opts.url || opts.path\n"
                   "      if (path === '/' && prefix.length > 0) {\n"
                   "        path = ''\n"
                   "      } else if (path[0] === '/' && prefix.endsWith('/')) {\n"
                   "        path = path.slice(1)\n"
                   "      }\n"
                   "      const url = prefix + path\n")

# Base afterRouteAdded block (NO stripping — double slash for trailing-slash prefixes).
BASE_AFTERROUTE = ("      // NEAR-MISS A: route path construction reverted to base (no strip)\n"
                    "      const path = opts.url || opts.path\n"
                    "      const url = prefix + (path === '/' && prefix.length > 0 ? '' : path)\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    if GOLD_AFTERROUTE not in t:
        print("near-miss A: gold afterRouteAdded block not found (is gold applied?)"); return 1
    p.write_text(t.replace(GOLD_AFTERROUTE, BASE_AFTERROUTE, 1))
    print("near-miss A (fix only buildRoutePrefix, revert afterRouteAdded) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
