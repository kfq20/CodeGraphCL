"""Near-miss A for fastify route_404: route 404 to notFound but DON'T reset sent/_isError flags.

The gold notFound() resets reply.sent=false and reply._isError=false before invoking the 404
context handler, because the error path already set sent=true/_isError=true and the notFound
handler's reply.send() would be a no-op (or re-enter the error path) without the reset. This
near-miss keeps the 404 routing but drops the resets — plausible "the flags are already set, no
need to touch them" — so the notFound handler's send() is a no-op and the response body is wrong.
Caught.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_r404_noreset.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = ("function notFound (reply) {\n"
       "  reply.sent = false\n"
       "  reply._isError = false\n\n")
NEW = ("function notFound (reply) {\n"
       "  // NEAR-MISS A: don't reset sent/_isError (re-entrancy not handled)\n\n")


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: notFound reset lines not found (is gold applied?)"); return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (route to notFound but don't reset sent/_isError) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
