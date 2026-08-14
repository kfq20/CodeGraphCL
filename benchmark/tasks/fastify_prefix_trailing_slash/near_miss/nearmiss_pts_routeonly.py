"""Near-miss B for fastify_prefix_trailing_slash: fix ONLY afterRouteAdded (the route path
construction), leave buildRoutePrefix (the nested plugin prefix construction) at the base
behavior.

The gold fixes BOTH join sites: buildRoutePrefix (nested plugin prefix) and afterRouteAdded
(route path). This near-miss keeps the afterRouteAdded fix (the route path join is correct)
but reverts buildRoutePrefix to base — so the nested plugin's prefix '/inner/' combined with
the outer '/v1/' produces '/v1//inner/' (double slash in the prefix). Routes inside '/inner/'
have the right path relative to '/v1//inner/' but the full URL '/v1//inner/route2' doesn't
match incoming '/v1/inner/route2'. Plausible "I fixed the route path join, the prefix join is
fine" — but the prefix join still produces a double slash. Caught.

Distinct from A: A reverts afterRouteAdded (route path), so the outer route fails; B reverts
buildRoutePrefix (nested prefix), so the nested route fails on a different assertion.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_pts_routeonly.py <repo_dir>
"""
import sys
from pathlib import Path

# Gold-applied buildRoutePrefix block (WITH the trailing-slash fix).
GOLD_BUILDPREFIX = ("    if (instancePrefix.endsWith('/')) {\n"
                    "      if (pluginPrefix[0] === '/') {\n"
                    "        pluginPrefix = pluginPrefix.slice(1)\n"
                    "      }\n"
                    "    } else if (pluginPrefix[0] !== '/') {\n"
                    "      pluginPrefix = '/' + pluginPrefix\n"
                    "    }\n"
                    "\n"
                    "    return instancePrefix + pluginPrefix\n")

# Base buildRoutePrefix block (NO trailing-slash handling — double slash for nested prefixes).
BASE_BUILDPREFIX = ("    // NEAR-MISS B: prefix construction reverted to base (no strip)\n"
                    "    if (pluginPrefix[0] !== '/') {\n"
                    "      pluginPrefix = '/' + pluginPrefix\n"
                    "    }\n"
                    "    return instancePrefix + pluginPrefix\n")


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    if GOLD_BUILDPREFIX not in t:
        print("near-miss B: gold buildRoutePrefix block not found (is gold applied?)"); return 1
    p.write_text(t.replace(GOLD_BUILDPREFIX, BASE_BUILDPREFIX, 1))
    print("near-miss B (fix only afterRouteAdded, revert buildRoutePrefix) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
