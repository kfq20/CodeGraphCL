"""Near-miss A for fastify_404_route_handler: intercept the 404 but don't switch the context.

The gold notFound() function switches reply.context to the registered 404 handler's context
(reply.context._fastify._404Context) and calls that handler. This near-miss keeps the intercept
but only sets the status code to 404 WITHOUT switching to the 404 handler's context — plausible
reasoning "a 404 just means set the status to 404". The test asserts the custom 404 handler's
body ('this was not found') is sent; without switching the context the generic error body (JSON
error) is sent instead, so the body assertion fails.

Distinct from near-miss B: A switches nothing (wrong handler); B switches the context but keeps
stale sent/_isError flags (aborts resend). Different assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_404_nocontextswitch.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = (
    "function notFound (reply) {\n"
    "  reply.sent = false\n"
    "  reply._isError = false\n"
    "\n"
    "  if (reply.context._fastify === null) {\n"
    "    reply.res.log.warn('Trying to send a NotFound error inside a 404 handler. Sending basic 404 response.')\n"
    "    reply.code(404).send('404 Not Found')\n"
    "    return\n"
    "  }\n"
    "\n"
    "  reply.context = reply.context._fastify._404Context\n"
    "  reply.context.handler(reply.request, reply)\n"
    "}"
)

NEW = (
    "function notFound (reply) {\n"
    "  reply.sent = false\n"
    "  reply._isError = false\n"
    "\n"
    "  if (reply.context._fastify === null) {\n"
    "    reply.res.log.warn('Trying to send a NotFound error inside a 404 handler. Sending basic 404 response.')\n"
    "    reply.code(404).send('404 Not Found')\n"
    "    return\n"
    "  }\n"
    "\n"
    "  // NEAR-MISS A: set the 404 status but do NOT switch to the 404 handler's context\n"
    "  reply.code(404)\n"
    "}"
)


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: notFound body not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (intercept 404 but don't switch to 404 context) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
