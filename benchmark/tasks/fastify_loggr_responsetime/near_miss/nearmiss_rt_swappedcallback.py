"""Near-miss A for fastify_loggr_responsetime: correct the hasLogger flag but swap the callback
selection (silence the response callback when logging is on).

The gold selects the real response-completion callback when a logger is present
(`hasLogger ? loggerUtils.onResponseCallback : noop`). This near-miss keeps the hasLogger flag
correctly initialized but INVERTS the selection — plausible reasoning "when logging is on, avoid
extra callback overhead / noise". The real callback never runs, so the "request completed" log
line carries no responseTime field, and `t.ok(line.responseTime)` fails.

Distinct from near-miss B: A breaks whether the callback runs at all (field absent); B breaks
the computed value (field present but 0/falsy). Different assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_rt_swappedcallback.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = "  const onResponseCallback = hasLogger ? loggerUtils.onResponseCallback : noop"
NEW = "  const onResponseCallback = hasLogger ? noop : loggerUtils.onResponseCallback  // NEAR-MISS A: inverted selection"


def main():
    p = Path(sys.argv[1]) / "fastify.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: onResponseCallback selection not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (swap callback selection: noop when logging) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
