"""Near-miss B for fastify_404_route_handler: switch context but don't reset sent/_isError.

The gold notFound() function resets reply.sent=false and reply._isError=false BEFORE switching to
the 404 handler's context and calling it. This near-miss switches the context correctly but does
NOT reset the flags — plausible reasoning "the flags don't matter; switching context is enough".
But the stale sent=true / _isError=true flags make the reply's send path abort early (it thinks
the response was already sent / is mid-error), so the 404 handler's body never reaches the wire.
The test asserts the custom handler's body ('this was not found') is sent; with stale flags the
body is wrong, so the assertion fails.

Distinct from near-miss A: A switches nothing (wrong handler); B switches context but keeps
stale flags (aborts resend). Different assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_404_noflagreset.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = (
    "function notFound (reply) {\n"
    "  reply.sent = false\n"
    "  reply._isError = false\n"
    "\n"
    "  if (reply.context._fastify === null) {\n"
)

NEW = (
    "function notFound (reply) {\n"
    "  // NEAR-MISS B: do NOT reset sent/_isError before switching to the 404 context\n"
    "\n"
    "  if (reply.context._fastify === null) {\n"
)


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: notFound body not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (switch context but don't reset sent/_isError) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
