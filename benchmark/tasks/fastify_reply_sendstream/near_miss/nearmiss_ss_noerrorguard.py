"""Near-miss A for fastify_reply_sendstream: no pre-headers-sent error guard (always destroy).

The gold sendStream() guards a source error by checking res.headersSent: if headers are NOT
sent, it delegates to handleError (so a 404-bearing stream yields a 404 JSON response); if
already sent, it destroys the response. This near-miss removes the guard and ALWAYS destroys the
response on a source error — plausible reasoning "a stream error means the response is dead,
just tear it down". A 404-bearing stream now destroys the connection (ECONNRESET) instead of
returning a 404, so the statusCode and content-type assertions fail.

Distinct from near-miss B: A destroys (ECONNRESET, no status); B sets the status directly but
skips the error handler (wrong content-type). Different assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_ss_noerrorguard.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = (
    "    sourceOpen = false\n"
    "    if (err) {\n"
    "      if (res.headersSent) {\n"
    "        res.log.error(err, 'response terminated with an error with headers already sent')\n"
    "        res.destroy()\n"
    "      } else {\n"
    "        handleError(reply, err)\n"
    "      }\n"
    "    }\n"
)

NEW = (
    "    sourceOpen = false\n"
    "    if (err) {\n"
    "      // NEAR-MISS A: always destroy, never delegate to the error handler\n"
    "      res.log.error(err, 'response terminated with an error with headers already sent')\n"
    "      res.destroy()\n"
    "    }\n"
)


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss A: source-eos callback not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss A (no pre-headers error guard, always destroy) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
