"""Near-miss B for fastify_loggr_responsetime: guard the wrong way (default responseTime to 0 and
never compute it).

The gold onResponseCallback guards an undefined _startTime by defaulting responseTime to 0 and
only computing `now() - res._startTime` when _startTime is set. This near-miss keeps the default
of 0 but INVERTS the guard so the compute branch never runs — plausible reasoning "default to 0
and skip the compute to avoid a NaN when _startTime is missing". The callback runs and logs a
responseTime field, but it is always 0 (falsy), so `t.ok(line.responseTime)` fails.

Distinct from near-miss A: A breaks whether the callback runs (field absent); B breaks the value
(field present but 0/falsy). Different assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_rt_noguardstarttime.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = (
    "  var responseTime = 0\n"
    "\n"
    "  if (res._startTime) {\n"
    "    responseTime = now() - res._startTime\n"
    "  }\n"
)
NEW = (
    "  var responseTime = 0\n"
    "\n"
    "  // NEAR-MISS B: inverted guard -> never compute, responseTime stays 0\n"
    "  if (!res._startTime) {\n"
    "    responseTime = now() - res._startTime\n"
    "  }\n"
)


def main():
    p = Path(sys.argv[1]) / "lib/logger.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: onResponseCallback body not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (inverted _startTime guard -> responseTime always 0) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
