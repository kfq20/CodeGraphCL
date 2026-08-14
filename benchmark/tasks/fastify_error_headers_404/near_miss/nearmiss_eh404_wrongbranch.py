"""Near-miss B for fastify_error_headers_404: move the headers call but to the wrong branch —
inside the `error.status >= 400` block but AFTER the `error.status === 404` check and return.

The gold moves reply.headers(error.headers) to the top of `if (error != null)`, before the
status-code checks. This near-miss removes the early block and instead inserts the headers call
inside the `if (error.status >= 400)` block, but after the `if (error.status === 404) {
notFound(reply); return }` check. Plausible "I moved it into the status block where the error
status is checked" — but for 404 errors, notFound() returns before the headers line runs, so the
response is sent without x-foo. FAILS. Caught.

Distinct from A: A doesn't move at all (headers in original late position); B moves but to a
position still after the 404 return. Both x-foo missing for 404, different reason.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_eh404_wrongbranch.py <repo_dir>
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

# The 404 check inside `error.status >= 400` branch. On gold:
#     if (error.status >= 400) {
#       if (error.status === 404) {
#         notFound(reply)
#         return
#       }
#       statusCode = error.status
#     } else if ...
ANCHOR = ("    if (error.status >= 400) {\n"
          "      if (error.status === 404) {\n"
          "        notFound(reply)\n"
          "        return\n"
          "      }\n"
          "      statusCode = error.status\n")

# Insert the headers call AFTER the 404 return but before statusCode assignment.
ANCHOR_WITH_MISPLACED = ("    if (error.status >= 400) {\n"
                         "      if (error.status === 404) {\n"
                         "        notFound(reply)\n"
                         "        return\n"
                         "      }\n"
                         "      // NEAR-MISS B: headers set here (after 404 return, too late)\n"
                         "      if (error.headers !== undefined) {\n"
                         "        reply.headers(error.headers)\n"
                         "      }\n"
                         "      statusCode = error.status\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if GOLD_EARLY not in t:
        print("near-miss B: gold early-headers block not found (is gold applied?)"); return 1
    if ANCHOR not in t:
        print("near-miss B: status>=400 anchor not found (is gold applied?)"); return 1
    t = t.replace(GOLD_EARLY, EARLY_REVERTED, 1)
    t = t.replace(ANCHOR, ANCHOR_WITH_MISPLACED, 1)
    p.write_text(t)
    print("near-miss B (move headers to status block but after 404 return) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
