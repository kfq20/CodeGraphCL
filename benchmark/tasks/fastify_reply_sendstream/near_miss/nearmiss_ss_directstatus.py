"""Near-miss B for fastify_reply_sendstream: set the status directly, skip the error handler.

The gold sendStream() delegates a pre-headers-sent source error to handleError, which sets the
status code, logs, applies error headers, AND serializes the error to a JSON body with the
application/json content-type. This near-miss sets the status code directly and ends the
response — plausible reasoning "a 404 stream error just needs a 404 status, skip the machinery".
The status IS 404, but the body/content-type are NOT the error handler's JSON output, so the
content-type assertion (application/json) fails.

Distinct from near-miss A: A destroys (ECONNRESET, no status at all); B sets the status but
wrong content-type. Different assertion fails.

Runs on HOST. near_miss_base: gold.
Usage: python3 nearmiss_ss_directstatus.py <repo_dir>
"""
import sys
from pathlib import Path

OLD = (
    "      if (res.headersSent) {\n"
    "        res.log.error(err, 'response terminated with an error with headers already sent')\n"
    "        res.destroy()\n"
    "      } else {\n"
    "        handleError(reply, err)\n"
    "      }\n"
)

NEW = (
    "      if (res.headersSent) {\n"
    "        res.log.error(err, 'response terminated with an error with headers already sent')\n"
    "        res.destroy()\n"
    "      } else {\n"
    "        // NEAR-MISS B: set status directly, skip the error handler (no JSON content-type)\n"
    "        res.statusCode = (err && (err.statusCode || err.status)) || 500\n"
    "        res.end()\n"
    "      }\n"
)


def main():
    p = Path(sys.argv[1]) / "lib/reply.js"
    t = p.read_text()
    if OLD not in t:
        print("near-miss B: source-eos error branch not found (is gold applied?)")
        return 1
    p.write_text(t.replace(OLD, NEW, 1))
    print("near-miss B (set status directly, skip handleError -> wrong content-type) injected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
