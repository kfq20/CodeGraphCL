"""Near-miss A for fastify_error_headers_404: don't move the headers call — revert to the
original position (after the log block, before customErrorHandler).

The gold moves reply.headers(error.headers) from after the log block to the top of the
`if (error != null)` block (before the status-code checks). This near-miss removes the early
block and re-adds the old block in the original position. Plausible "the original position is
fine — headers are set before the custom error handler for non-404 errors" — but for 404
errors, notFound() is called in the status-code check and returns before the log block, so the
headers are never set. The test's 404 response is missing x-foo. FAILS. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_eh404_nomove.py <repo_dir>
"""
import sys
from pathlib import Path

# The gold's early block (inside `if (error != null)`, before status checks).
GOLD_EARLY = ("  if (error != null) {\n"
              "    if (error.headers !== undefined) {\n"
              "      reply.headers(error.headers)\n"
              "    }\n")

# Revert: just the `if (error != null) {` line, no headers block.
EARLY_REVERTED = ("  if (error != null) {\n")

# The anchor where the old block should be re-inserted (after log block, before customErrorHandler).
# On gold, the old block was removed, so this anchor is:
#   ...log.info line...
#   <blank>
#   var customErrorHandler = reply.context.errorHandler
ANCHOR = ("    res.log.info({ res: res, err: error }, error && error.message)\n"
          "  }\n"
          "\n"
          "  var customErrorHandler = reply.context.errorHandler\n")

# Re-insert the old block before customErrorHandler.
ANCHOR_WITH_OLD = ("    res.log.info({ res: res, err: error }, error && error.message)\n"
                   "  }\n"
                   "\n"
                   "  // NEAR-MISS A: headers set in original position (after log, before handler)\n"
                   "  if (error && error.headers) {\n"
                   "    reply.headers(error.headers)\n"
                   "  }\n"
                   "\n"
                   "  var customErrorHandler = reply.context.errorHandler\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if GOLD_EARLY not in t:
        print("near-miss A: gold early-headers block not found (is gold applied?)"); return 1
    if ANCHOR not in t:
        print("near-miss A: before-handler anchor not found (is gold applied?)"); return 1
    t = t.replace(GOLD_EARLY, EARLY_REVERTED, 1)
    t = t.replace(ANCHOR, ANCHOR_WITH_OLD, 1)
    p.write_text(t)
    print("near-miss A (don't move headers call, leave in original position) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
