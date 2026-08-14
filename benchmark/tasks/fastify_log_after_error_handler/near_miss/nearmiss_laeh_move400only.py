"""Near-miss B for fastify_log_after_error_handler: move ONLY the 400-level log block after
customErrorHandler, leave the 500-level block BEFORE it.

The gold moves BOTH the statusCode>=500 and statusCode>=400 log blocks after the
customErrorHandler check. This near-miss moves only the 400 block — plausible "the 400 is
the one the test checks, 500 can stay" — but the 500-level test still sees the ERROR log
BEFORE the handler, so the log order is still wrong for 500 errors. Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_laeh_move400only.py <repo_dir>
"""
import sys
from pathlib import Path

GOLD_AFTER = ("  if (statusCode >= 500) {\n"
              "    res.log.error({ req: reply.request.raw, res: res, err: error }, error && error.message)\n"
              "  } else if (statusCode >= 400) {\n"
              "    res.log.info({ req: reply.request.raw, res: res, err: error }, error && error.message)\n"
              "  }\n")

SPLIT_AFTER = ("  // NEAR-MISS B: 500-level log left before customErrorHandler\n"
               "  if (statusCode >= 400) {\n"
               "    res.log.info({ req: reply.request.raw, res: res, err: error }, error && error.message)\n"
               "  }\n")

BEFORE_HANDLER = ("  res.statusCode = statusCode\n\n"
                  "  // NEAR-MISS B: 500-level log emitted before customErrorHandler\n"
                  "  if (statusCode >= 500) {\n"
                  "    res.log.error({ req: reply.request.raw, res: res, err: error }, error && error.message)\n"
                  "  }\n\n"
                  "  var customErrorHandler = reply.context.errorHandler\n")

ORIGINAL_BEFORE = ("  res.statusCode = statusCode\n\n"
                   "  var customErrorHandler = reply.context.errorHandler\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if GOLD_AFTER not in t:
        print("near-miss B: gold after-block not found (is gold applied?)"); return 1
    if ORIGINAL_BEFORE not in t:
        print("near-miss B: before-handler anchor not found (is gold applied?)"); return 1
    t = t.replace(GOLD_AFTER, SPLIT_AFTER, 1)
    t = t.replace(ORIGINAL_BEFORE, BEFORE_HANDLER, 1)
    p.write_text(t)
    print("near-miss B (move only 400 block, leave 500 before handler) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
