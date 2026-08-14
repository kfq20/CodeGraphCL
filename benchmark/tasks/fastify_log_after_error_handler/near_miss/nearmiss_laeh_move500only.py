"""Near-miss A for fastify_log_after_error_handler: move ONLY the 500-level log block after
customErrorHandler, leave the 400-level block BEFORE it.

The gold moves BOTH the statusCode>=500 and statusCode>=400 log blocks after the
customErrorHandler check. This near-miss moves only the 500 block — plausible "the 500 is
the important one, 400 is just info" — but the 400-level test still sees the log BEFORE the
handler, so the handler's 400 response still has a pre-handler ERROR-level log entry. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_laeh_move500only.py <repo_dir>
"""
import sys
from pathlib import Path

# On gold: both blocks are AFTER customErrorHandler. We need to move the 400 block back BEFORE.
# Gold state: the block after customErrorHandler return is:
#   if (statusCode >= 500) { ... } else if (statusCode >= 400) { ... }
# We split: remove the 400 branch from after, re-insert a standalone 400 log BEFORE
# customErrorHandler.

GOLD_AFTER = ("  if (statusCode >= 500) {\n"
              "    res.log.error({ req: reply.request.raw, res: res, err: error }, error && error.message)\n"
              "  } else if (statusCode >= 400) {\n"
              "    res.log.info({ req: reply.request.raw, res: res, err: error }, error && error.message)\n"
              "  }\n")

SPLIT_AFTER = ("  if (statusCode >= 500) {\n"
               "    res.log.error({ req: reply.request.raw, res: res, err: error }, error && error.message)\n"
               "  }\n"
               "  // NEAR-MISS A: 400-level log left before customErrorHandler\n")

BEFORE_HANDLER = ("  res.statusCode = statusCode\n\n"
                  "  // NEAR-MISS A: 400-level log emitted before customErrorHandler\n"
                  "  if (statusCode >= 400) {\n"
                  "    res.log.info({ req: reply.request.raw, res: res, err: error }, error && error.message)\n"
                  "  }\n\n"
                  "  var customErrorHandler = reply.context.errorHandler\n")

ORIGINAL_BEFORE = ("  res.statusCode = statusCode\n\n"
                   "  var customErrorHandler = reply.context.errorHandler\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if GOLD_AFTER not in t:
        print("near-miss A: gold after-block not found (is gold applied?)"); return 1
    if ORIGINAL_BEFORE not in t:
        print("near-miss A: before-handler anchor not found (is gold applied?)"); return 1
    t = t.replace(GOLD_AFTER, SPLIT_AFTER, 1)
    t = t.replace(ORIGINAL_BEFORE, BEFORE_HANDLER, 1)
    p.write_text(t)
    print("near-miss A (move only 500 block, leave 400 before handler) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
